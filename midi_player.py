import threading
import time
import mido
import random
from pyo import HarmTable, CurveTable, Osc, Adsr, midiToHz, Server, SigTo

class MidiPlayer:
    def __init__(self, midi_file: str, server: Server, wave_type="sine", pulse_width=0.5, phase=0.0, coarse=0):
        # --- MIDI / pyo ---
        self.mid = mido.MidiFile(midi_file)
        self.server = server

        self._pulse_width = pulse_width
        self.phase = float(phase)                      # float - do UI / logiki
        self.phase_sig = SigTo(self.phase, time=0.01)  # SigTo - dla pyo
        self.random_phase = False
        self._current_phase_value = float(phase)

        # --- tables ---
        self.custom_table = CurveTable(list=[(0, 0), (1023, 0)], size=1024)
        self.square_table = self._create_square_table(self._pulse_width)
        self.tables = {
            "sine": HarmTable([1]),
            "square": self.square_table,
            "saw": HarmTable([1/float(n) for n in range(1, 50)]),
            "triangle": HarmTable([1/float(n**2) if n % 2 != 0 else 0 for n in range(1, 50)]),
            "hand": self.custom_table
        }
        self._wave_type = wave_type if wave_type in self.tables else "sine"

        # --- poly / mono voices ---
        self.active_notes = {}    # note -> (osc, env)
        self.lock = threading.Lock()

        # --- coarse (semitones) ---
        self._coarse = 0
        self._fine = 0.0
        self.set_coarse(coarse)

        # ADSR
        self._attack = 0.01
        self._decay = 0.05
        self._sustain = 0.7
        self._release = 0.2


        # Mono / Legato / Portamento
        self.mono = False
        self.legato = False
        self.portamento_time = 0.0
        self.portamento_mode = "always"   # "always" or "legato"
        self.poly_portamento = False

        # Mono state
        self.pressed_notes = set()
        self.current_mono_note = None
        self.mono_osc = None
        self.mono_env = None
        self.mono_freq = None

        # Poly helper
        self.last_poly_freq = None

        # thread control
        self.thread = None
        self.stop_thread = False

    def _create_square_table(self, pulse_width):
        pulse_width = float(pulse_width)
        if not (0 < pulse_width < 1):
            pulse_width = 0.5
        pos = max(1, int(1024 * pulse_width))
        return CurveTable(list=[(0, 1), (pos-1, 1), (pos, 0), (1023, 0)], size=1024)

    @property
    def pulse_width(self):
        return self._pulse_width

    @pulse_width.setter
    def pulse_width(self, value):
        value = float(value)
        if 0 < value < 1 and self._pulse_width != value:
            self._pulse_width = value
            pos = max(1, int(1024 * self._pulse_width))
            new_list = [(0, 1), (pos - 1, 1), (pos, 0), (1023, 0)]
            try:
                self.square_table.replace(new_list)
            except Exception:
                self.square_table = self._create_square_table(self._pulse_width)
                self.tables["square"] = self.square_table
            
            with self.lock:
                for osc, env in self.active_notes.values():
                    try: osc.table = self.square_table
                    except: pass
                if self.mono_osc is not None:
                    try: self.mono_osc.table = self.square_table
                    except: pass    

    def set_phase(self, v):
        try:
            v = max(0.0, min(1.0, float(v)))
        except Exception:
            return
        self.phase = v
        try:
            self.phase_sig.setValue(v)
        except Exception:
            # jeśli pyo jeszcze nie wystartowało lub coś innego - ignorujemy
            pass
        # jeśli random jest off — synchronizujemy current value
        if not self.random_phase:
            self._current_phase_value = v

    def set_random_phase(self, enabled: bool):
        self.random_phase = bool(enabled)

    def _get_note_phase(self):
        # wywołuj tę metodę wtedy, gdy chcesz ZMIENIĆ phase (np. na NOTE ON)
        if self.random_phase:
            self._current_phase_value = random.random()
        else:
            self._current_phase_value = float(self.phase)

        # aktualizujemy SigTo (audio) — niech audio używa tej wartości
        try:
            self.phase_sig.setValue(self._current_phase_value)
        except Exception:
            pass

        # zwracamy SigTo — Osc może dostać obiekt pyo
        return self.phase_sig
    
    def get_current_phase_value(self):
        return float(getattr(self, "_current_phase_value", self.phase))



    def update_table(self, points):
        try:
            safe_points = [(int(p[0]), float(p[1])) for p in points]
            self.custom_table.list = safe_points
            if self._wave_type == "hand":
                with self.lock:
                    for osc, env in self.active_notes.values():
                        try: osc.table = self.custom_table
                        except: pass
                    if self.mono_osc is not None:
                        try: self.mono_osc.table = self.custom_table
                        except: pass
        except Exception:
            pass

    @property
    def wave_type(self):
        return self._wave_type

    @wave_type.setter
    def wave_type(self, value):
        if value in self.tables and self._wave_type != value:
            self._wave_type = value
            with self.lock:
                new_table = self.tables[value]
                for osc, env in self.active_notes.values():
                    try: osc.table = new_table
                    except: pass
                if self.mono_osc is not None:
                    try: self.mono_osc.table = new_table
                    except: pass

    # --- COARSE / FINE ---
    def _semitone_factor(self, semitones):
        try:
            return 2.0 ** (float(semitones) / 12.0)
        except Exception:
            return 1.0

    @property
    def coarse(self):
        return self._coarse

    def _compute_final_freq(self, note):
        try:
            base = float(midiToHz(int(note)))
        except Exception:
            return None
        coarse_factor = self._semitone_factor(self._coarse)
        fine_factor = 2 ** (self._fine / 1200.0)
        return base * coarse_factor * fine_factor

    def set_coarse(self, semitones: float):
        try:
            s = float(semitones)
        except Exception:
            return
        if s > 24: s = 24.0
        if s < -24: s = -24.0
        with self.lock:
            if self._coarse == s:
                return
            self._coarse = s
            # aktualizacja poly
            for note, (osc, env) in list(self.active_notes.items()):
                try:
                    final = self._compute_final_freq(note)
                    if final is not None: osc.freq = final
                except: pass
            # aktualizacja mono
            if self.mono_osc is not None and self.current_mono_note is not None:
                try:
                    final = self._compute_final_freq(self.current_mono_note)
                    if final is not None:
                        self.mono_freq = final
                        self.mono_osc.freq = final
                except: pass
            self.last_poly_freq = None

    @property
    def fine(self):
        return self._fine

    def set_fine(self, cents: float):
        try:
            c = float(cents)
        except:
            return
        if c > 100: c = 100
        if c < -100: c = -100

        with self.lock:
            if self._fine == c:
                return
            self._fine = c
            for note, (osc, env) in list(self.active_notes.items()):
                try:
                    final = self._compute_final_freq(note)
                    if final is not None: osc.freq = final
                except: pass
            if self.mono_osc is not None and self.current_mono_note is not None:
                try:
                    final = self._compute_final_freq(self.current_mono_note)
                    if final is not None:
                        self.mono_freq = final
                        self.mono_osc.freq = final
                except: pass
            self.last_poly_freq = None

    @fine.setter
    def fine(self, cents: float):
        self.set_fine(cents)

    @coarse.setter
    def coarse(self, semitones: float):
        self.set_coarse(semitones)

    # --- SETTERS (MONO/LEGATO/PORTAMENTO) ---
    def set_mono(self, enabled: bool):

        with self.lock:
            enabled = bool(enabled)

            # Если режим не изменился — ничего не делаем
            if self.mono == enabled:
                return

            self.mono = enabled

            if not self.mono:
                # Отключаем mono: останавливаем моно-огибающую и осциллятор
                if self.mono_env is not None:
                    try: self.mono_env.stop()
                    except: pass
                if self.mono_osc is not None:
                    try: self.mono_osc.stop()
                    except: pass

                self.mono_osc = None
                self.mono_env = None
                self.mono_freq = None
                self.current_mono_note = None
                # wyczyszczamy nabór nót
                self.pressed_notes.clear()
                return

            # --- wlączmy mono ---
            for osc, env in list(self.active_notes.values()):
                try: env.stop()
                except: pass
                try: osc.stop()
                except: pass
            self.active_notes.clear()

            if self.pressed_notes:
                highest = max(self.pressed_notes)
                self.pressed_notes = {highest}
                self.current_mono_note = highest

                final = self._compute_final_freq(highest)
                if final is None:
                    try:
                        final = float(midiToHz(highest)) * self._semitone_factor(self._coarse)
                    except Exception:
                        final = None

                self.mono_freq = final

                try:
                    current_table = self.tables.get(self._wave_type, self.custom_table)
                    env = Adsr(attack=float(self.attack), decay=float(self.decay),
                            sustain=float(self.sustain), release=float(self._release),
                            mul=0.3)
                    osc = Osc(table=current_table,
                            freq=(final if final is not None else 440.0),
                            phase=self._get_note_phase(),
                            mul=[env, env]).out()
                    self.mono_env = env
                    self.mono_osc = osc

                    try: self.mono_env.play()
                    except: pass
                except Exception:
                    # jesli cos poszlo nie tak - wylaczamy
                    try:
                        if self.mono_env is not None: self.mono_env.stop()
                    except: pass
                    try:
                        if self.mono_osc is not None: self.mono_osc.stop()
                    except: pass
                    self.mono_env = None
                    self.mono_osc = None
                    self.mono_freq = None
                    self.current_mono_note = None
            else:

                self.mono_osc = None
                self.mono_env = None
                self.mono_freq = None
                self.current_mono_note = None
                
    def set_legato(self, enabled: bool):
        with self.lock:
            self.legato = bool(enabled)

    def set_portamento(self, time_sec: float, mode: str = "always"):
        with self.lock:
            self.portamento_time = max(0.0, float(time_sec))
            if mode in ("always", "legato"):
                self.portamento_mode = mode

    def set_poly_portamento(self, enabled: bool):
        with self.lock:
            self.poly_portamento = bool(enabled)

    # --- GLIDE ---
    def _start_glide(self, osc, start_freq, target_freq, glide_time):
        try:
            if glide_time <= 0 or start_freq == target_freq:
                osc.freq = target_freq
                return
            steps = max(6, int(60 * glide_time))
            for i in range(1, steps + 1):
                t = i / float(steps)
                new_freq = start_freq + (target_freq - start_freq) * t
                try: osc.freq = new_freq
                except: pass
                time.sleep(glide_time / steps)
            try: osc.freq = target_freq
            except: pass
        except Exception:
            pass

    def _play_loop(self):
        try:
            while not self.stop_thread:
                # Odtwarzanie pliku MIDI
                for msg in self.mid.play():
                    if self.stop_thread:
                        break

                    # --- NOTE ON ---
                    if msg.type == "note_on" and getattr(msg, "velocity", 0) > 0:
                        note = int(msg.note)
                        base_freq = float(midiToHz(note))
                        factor = self._semitone_factor(self._coarse)
                        freq = base_freq * factor
                        current_table = self.tables[self._wave_type]

                        # --- POLY MODE ---
                        if not self.mono:
                            env = Adsr(attack=float(self.attack), decay=float(self.decay),
                                       sustain=float(self.sustain), release=float(self._release),
                                       mul=0.3).play()
                            
                            start_freq = self.last_poly_freq if (self.poly_portamento and self.last_poly_freq is not None) else freq
                            osc = Osc(table=current_table, phase=self._get_note_phase(), 
                                      freq=start_freq, mul=[env, env]).out()
                            
                            if self.poly_portamento and self.portamento_time > 0:
                                threading.Thread(target=self._start_glide, args=(osc, start_freq, freq, self.portamento_time), daemon=True).start()
                            else:
                                osc.freq = freq
                                
                            self.last_poly_freq = freq
                            with self.lock:
                                self.active_notes[note] = (osc, env)

                        # --- MONO MODE ---
                        else:
                            with self.lock:
                                self.pressed_notes.add(note)
                                new_note = max(self.pressed_notes)
                                prev_note = self.current_mono_note # Stan przed tą nutą
                                
                                if self.mono_osc is None:
                                    env = Adsr(attack=float(self.attack), decay=float(self.decay),
                                               sustain=float(self.sustain), release=float(self._release),
                                               mul=0.3)
                                    osc = Osc(table=current_table, freq=freq, 
                                              phase=self._get_note_phase(), mul=[env, env]).out()
                                    self.mono_osc = osc
                                    self.mono_env = env
                                    self.mono_freq = freq
                                    # Start dźwięku
                                    self.mono_env.play()
                                else:
                                    # REUSE: Oscylator już istnieje
                                    if prev_note is None:
                                        # Poprzednio cisza -> świeży atak
                                        self.mono_osc.freq = freq
                                        self.mono_freq = freq
                                        self.mono_env.play()
                                    else:
                                        # Legato
                                        should_glide = (self.portamento_mode == "always") or (self.portamento_mode == "legato" and self.legato)
                                        start_f = self.mono_freq if self.mono_freq else freq
                                        
                                        if should_glide and self.portamento_time > 0:
                                            threading.Thread(target=self._start_glide, args=(self.mono_osc, start_f, freq, self.portamento_time), daemon=True).start()
                                        else:
                                            self.mono_osc.freq = freq
                                        
                                        self.mono_freq = freq
                                        
                                        if not self.legato:
                                            self.mono_env.play()
                                        # Jeśli legato, sustain trwa

                                self.current_mono_note = new_note

                    # --- NOTE OFF ---
                    elif msg.type == "note_off" or (msg.type == "note_on" and getattr(msg, "velocity", 0) == 0):
                        note = int(msg.note)
                        
                        # --- POLY OFF ---
                        if not self.mono:
                            with self.lock:
                                entry = self.active_notes.pop(note, None)
                            if entry:
                                osc, env = entry
                                try: env.stop()
                                except: pass
                                threading.Timer(float(self._release) + 0.1, osc.stop).start()

                        # --- MONO OFF ---
                        else:
                            with self.lock:
                                if note in self.pressed_notes:
                                    self.pressed_notes.remove(note)
                                
                                new_note = max(self.pressed_notes) if self.pressed_notes else None
                                
                                if new_note is None:
                                    # Puszczono wszystko -> Release
                                    if self.mono_env is not None:
                                        self.mono_env.stop()
                                    # NIE niszczymy oscylatora, czeka w tle
                                    self.current_mono_note = None
                                else:
                                    # Powrót do poprzedniej nuty
                                    factor = self._semitone_factor(self._coarse)
                                    target_freq = float(midiToHz(new_note)) * factor
                                    
                                    should_glide = (self.portamento_mode == "always") or (self.portamento_mode == "legato" and self.legato)
                                    start_f = self.mono_freq if self.mono_freq else target_freq
                                    
                                    if should_glide and self.portamento_time > 0 and self.mono_osc:
                                        threading.Thread(target=self._start_glide, args=(self.mono_osc, start_f, target_freq, self.portamento_time), daemon=True).start()
                                    else:
                                        if self.mono_osc: self.mono_osc.freq = target_freq
                                    
                                    self.mono_freq = target_freq
                                    self.current_mono_note = new_note
                                    
                                    if not self.legato and self.mono_env:
                                        self.mono_env.play()

                if not self.stop_thread:
                    pass

        except Exception as e:
            print("Błąd w pętli MIDI:", e)

    def stop(self):
        self.stop_thread = True
        with self.lock:
            # Poly cleanup
            for osc, env in self.active_notes.values():
                try: env.stop()
                except: pass
                try: osc.stop()
                except: pass
            self.active_notes.clear()

            # Mono cleanup
            if self.mono_osc is not None:
                try: self.mono_env.stop()
                except: pass
                try: self.mono_osc.stop()
                except: pass
            
            self.mono_osc = None
            self.mono_env = None
            self.mono_freq = None
            self.current_mono_note = None
            self.pressed_notes.clear()

    def play(self, wave_type=None, midi_file=None):
        if midi_file is not None:
            self.mid = mido.MidiFile(midi_file)
            self.stop_thread = True
            if self.thread and self.thread.is_alive():
                self.thread.join()
            self.stop_thread = False

        try:
            self.server.start()
        except Exception:
            pass

        if wave_type is not None and wave_type in self.tables:
            self._wave_type = wave_type

        if self.thread and self.thread.is_alive():
            return

        self.stop_thread = False
        self.thread = threading.Thread(target=self._play_loop, daemon=True)
        self.thread.start()

    def load_midi(self, midi_file: str):
        self.stop()
        try:
            self.mid = mido.MidiFile(midi_file)
        except Exception as e:
            print("Nie udało się załadować MIDI:", e)

    @property
    def release(self):
        return self._release
    

    # ADSR properties

    @property
    def attack(self):
        return self._attack

    @attack.setter
    def attack(self, value):
        try:
            v = max(0.0, float(value))
        except:
            return
        with self.lock:
            self._attack = v
            for _, env in list(self.active_notes.values()):
                try:
                    env.attack = v
                except:
                    try: env.setAttack(v)
                    except: pass
            if self.mono_env is not None:
                try:
                    self.mono_env.attack = v
                except:
                    try: self.mono_env.setAttack(v)
                    except: pass

    @property
    def decay(self):
        return self._decay

    @decay.setter
    def decay(self, value):
        try:
            v = max(0.0, float(value))
        except:
            return
        with self.lock:
            self._decay = v
            for _, env in list(self.active_notes.values()):
                try:
                    env.decay = v
                except:
                    try: env.setDecay(v)
                    except: pass
            if self.mono_env is not None:
                try:
                    self.mono_env.decay = v
                except:
                    try: self.mono_env.setDecay(v)
                    except: pass

    @property
    def sustain(self):
        return self._sustain

    @sustain.setter
    def sustain(self, value):
        try:
            v = float(value)
        except:
            return
        with self.lock:
            self._sustain = v
            for _, env in list(self.active_notes.values()):
                try:
                    env.sustain = v
                except:
                    try: env.setSustain(v)
                    except: pass
            if self.mono_env is not None:
                try:
                    self.mono_env.sustain = v
                except:
                    try: self.mono_env.setSustain(v)
                    except: pass

    @property
    def tbl(self):
        return self.custom_table

    @release.setter
    def release(self, value):
        self._release = max(0.001, float(value))
        with self.lock:
            for _, env in self.active_notes.values():
                try: env.release = float(self._release)
                except: pass
            if self.mono_env is not None:
                try: self.mono_env.release = float(self._release)
                except: pass