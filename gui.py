import cv2
import mediapipe as mp
import time
from cv2_button import Cv2Button
from cv2_toggle import Cv2Toggle
from cv2_counter import Cv2Counter
from midi_player import MidiPlayer
from hand_processor import HandProcessor
import re
import os
from pyo import Server, HarmTable
import threading
from cv2_slider import Cv2Slider


class MidiControllerGUI:
    def __init__(self):
        # inicjacja zmianych
        self._init_server()
        self._init_states()
        self._init_ui_components()
        self._init_final_states()

        self.slider_locked = False
        self.slider_release_locked = False
        self.slider_decay_locked = False
        self.slider_sustain_locked = False
        
        self.timer_wave_type = None
        self.timer_wave_type_sine = None
        self.timer_wave_type_squere = None
        self.timer_wave_type_saw = None
        self.timer_wave_type_tringle = None
        self.timer_wave_type_hand_control = None
        
        self.timer_pitch = None
        
        self.timer_slider_pw = None
        self.timer_slider_cents_zone = None
        
        self.semitones_counter_minus_timer = None
        self.semitones_counter_minus_last = None
        self.semitones_counter_plus_timer = None
        self.semitones_counter_plus_last = None
        
        self.octave_minus_timer = None
        self.octave_minus_last = None
        self.octave_plus_timer = None
        self.octave_plus_last = None
        
        # stany
        self.wave_type_state = "off"
        self.pitch_state = "off"
        self.phase_random_state = "off"
        self.glide_mode_always_state = "off"
        self.glide_mode_legato_state = "on"
        
        # dla Hand Control
        self.hand_wave = False
        self.hand_control = False
        self.last_fingers_pos = None
        self.still_timer = None
        self.fingers_are_still = False
        self.timer_hand_set = None
        
        # dla sliderów
        self.slider_cents_locked = False
        self.slider_cents_hold_timer = None
        self.slider_cents_last_ix = None
        self.slider_cents_stop_timer = None
        self.slider_cents_snap_value = None
        
        self.slider_pw_locked = False
        self.slider_pw_hold_timer = None
        self.slider_pw_last_ix = None
        self.slider_pw_stop_timer = None
        self.slider_pw_snap_value = None

    def _init_server(self):
        self.s = Server().boot()
        self.s.amp = 0.5
        self.s.start()
        
        # robimy 1 player
        self.player = MidiPlayer("XV.mid", server=self.s)
    
    def _init_states(self):
        self.sine = False
        self.squere = False
        self.saw = False
        self.tringle = False
        self.hand = False
        
        # punkty reki
        self.current_hand_points = []
        
        # timery i ich stany
        self.timer_start = None
        self.timer_wave = None
        self.timer_cancel = None
        self.timer_midi = None
        self.timer_down = None
        self.timer_up = None
        self.timer_midi_choice = None
        self.timer_midi_ok = None
        self.timer_adsr = None
        self.timer_adsr_reset = None
        self.timer_adsr_slider = None
        self.timer_adsr_slider_hold = None
        self.timer_fixed_ix = None
        self.slider_hold_timer = None
        self.slider_snap_value = None
        self.slider_last_ix = None
        self.slider_stop_timer = None
        self.timer_slider_zone = None
        
        self.timer_slider_release_zone = None
        self.slider_release_hold_timer = None
        self.slider_release_last_ix = None
        self.slider_release_stop_timer = None
        self.slider_release_snap_value = None
        
        self.timer_slider_decay_zone = None
        self.slider_decay_hold_timer = None
        self.slider_decay_last_ix = None
        self.slider_decay_stop_timer = None
        self.slider_decay_snap_value = None
        
        self.timer_slider_sustain_zone = None
        self.slider_sustain_hold_timer = None
        self.slider_sustain_last_ix = None
        self.slider_sustain_stop_timer = None
        self.slider_sustain_snap_value = None
        
        self.timer_wave_type_zone = None
        self.timer_wave_type_sine = None
        self.timer_wave_type_squere = None
        self.timer_wave_type_saw = None
        self.timer_wave_type_tringle = None
        self.timer_wave_type_hand_control = None
        self.timer_hand_set = None
        self.timer_pitch = None
        
        self.slider_pw_hold_timer = None
        self.slider_pw_snap_value = None
        self.slider_pw_last_ix = None
        self.slider_pw_stop_timer = None
        self.slider_pw_locked = False
        self.timer_slider_pw = None
        
        self.timer_semitones_slider_zone = None
        self.semitones_counter_plus_timer = None
        self.semitones_counter_minus_timer = None
        self.semitones_counter_minus_timer_last = None
        self.semitones_counter_plus_timer_last = None
        self.repeat_interval = 0.5
        
        self.octave_counter_plus_timer = None
        self.octave_counter_minus_timer = None
        self.octave_counter_minus_timer_last = None
        self.octave_counter_plus_timer_last = None
        
        self.timer_cents_zone = None
        self.slider_cents_timer = None
        self.slider_cents_last_ix = None
        self.slider_cents_stop_timer = None
        self.slider_cents_snap_value = None
        self.timer_cents_reset = None
        
        self.timer_mono_toggle = None
        self.timer_legato_toggle = None
        self.timer_poly_glide_toggle = None
        self.timer_glide_mode_legato = None
        self.timer_glide_mode_always = None
        
        self.timer_glide_time_zone = None
        self.slider_glide_time_timer = None
        self.slider_glide_time_last_ix = None
        self.slider_glide_time_stop_timer = None
        self.slider_glide_time_snap_value = None
        
        self.timer_phase_zone = None
        self.slider_phase_timer = None
        self.slider_phase_last_ix = None
        self.slider_phase_stop_timer = None
        self.slider_phase_snap_value = None
        self.timer_phase_random = None
        
        self.midi_button_row = 0


        self.timer_cents_reset = None
        self.timer_mono_toggle = None
        self.timer_legato_toggle = None
        self.timer_poly_glide_toggle = None
        self.timer_glide_mode_legato = None
        self.timer_glide_mode_always = None
        
        self.timer_glide_time_zone = None
        self.slider_glide_time_hold_timer = None
        self.slider_glide_time_last_ix = None
        self.slider_glide_time_stop_timer = None
        self.slider_glide_time_snap_value = None
        self.slider_glide_time_locked = False
        self.slider_active = False
        
        self.timer_slider_phase_zone = None
        self.slider_phase_hold_timer = None
        self.slider_phase_last_ix = None
        self.slider_phase_stop_timer = None
        self.slider_phase_snap_value = None
        self.slider_phase_locked = False
        
        self.timer_phase_random = None
        
        # dla okienka midi
        self.timer_midi = None
        self.timer_down = None
        self.timer_up = None
        self.timer_midi_ok = None
        self.timer_cancel = None
        self.active_button = None

        
        # spis midi
        self.project_path = os.path.dirname(os.path.abspath(__file__))
        self.midi_folder = os.path.join(self.project_path, "midi")
        self.midi = [f for f in os.listdir(self.midi_folder) 
                    if os.path.isfile(os.path.join(self.midi_folder, f))]
        self.midi.sort(key=self.extract_number)
    
    def extract_number(self, filename):
        match = re.match(r'^(\d+)', filename)
        return int(match.group(1)) if match else float('inf')
    
    def _init_ui_components(self):
        self.cap = cv2.VideoCapture(0)
        self.hp = HandProcessor(draw_lines=False, draw_rect=False, draw_fing=True)
        
        success, img = self.cap.read()
        if not success or img is None:
            self.h, self.w = 480, 640
        else:
            self.h, self.w, _ = img.shape

        
        self._init_main_buttons()
        self._init_midi_window_ui()
        self._init_wave_ui()
    
    def _init_main_buttons(self):
        # przycisk Play
        self.play_button = Cv2Button(
            label="play", 
            pos=(self.w-(self.w//6), 0), 
            size=(self.w//6, self.h//6), 
            alpha=0.6
        )
        self.play_x, self.play_y = self.play_button.pos
        self.play_size_w, self.play_size_h = self.play_button.size
        
        # przycisk MIDI
        self.midi_button = Cv2Button(
            label="midi", 
            pos=(self.w-(self.w//6), self.h//6), 
            size=(self.w//6, self.h//6), 
            alpha=0.6
        )
        self.midi_x, self.midi_y = self.midi_button.pos
        self.midi_size_w, self.midi_size_h = self.midi_button.size
    
    def _init_midi_window_ui(self):
        # okienko MIDI
        self.midi_window_button = Cv2Button(
            label="",
            pos=(self.w-self.w//2, 0),
            size=((self.w//2)-(self.w//6), self.h//2),
            alpha=0
        )
        
        # obliczenia koordynat midi plikow w MIDI
        button_w = (self.w//2) - (self.w//6)
        button_h = self.h // 16
        start_x = self.w - self.w//2
        start_y = 0
        
        self.midi_buttons = []
        self.rows = []
        i_midi = 0
        total_midi = len(self.midi)
        
        while i_midi < total_midi:
            remaining = total_midi - i_midi
            
            if i_midi == 0:
                count = 7
                y_offset = 0
            elif remaining <= 7:
                count = 7
                y_offset = button_h  # ostatni rzad
            else:
                count = 6
                y_offset = button_h  # rzedy pomiedzy
            
            row_buttons = []
            for j, label in enumerate(self.midi[i_midi:i_midi+count]):
                x = start_x
                y = start_y + y_offset + j * button_h
                
                btn = Cv2Button(
                    label=label,
                    pos=(x, y),
                    size=(button_w, button_h),
                    alpha=0.0
                )
                
                row_buttons.append(btn)
                self.midi_buttons.append(btn)
            
            self.rows.append(row_buttons)
            i_midi += count
        
        # przyciski nawigacji okienka midi down/up ok/cencel
        self.midi_window_down_button = Cv2Button(
            label="",
            pos=(self.w - self.w//2, self.h // 2 - self.h // 16),
            size=((self.w//2) - (self.w//6), self.h//18),
            alpha=0.0,
            draw_arrow=True,
            arrow_dir="down"
        )
        self.midi_down_x, self.midi_down_y = self.midi_window_down_button.pos
        self.midi_size_down_w, self.midi_size_down_h = self.midi_window_down_button.size
        
        self.midi_window_up_button = Cv2Button(
            label="",
            pos=(self.w - self.w//2, 0),
            size=((self.w//2) - (self.w//6), self.h//18),
            alpha=0.0,
            draw_arrow=True,
            arrow_dir="up"
        )
        self.midi_up_x, self.midi_up_y = self.midi_window_up_button.pos
        self.midi_size_up_w, self.midi_size_up_h = self.midi_window_up_button.size
        
        self.midi_window_ok_button = Cv2Button(
            label="ok",
            pos=((self.w//2), self.h//2),
            size=(((self.w//2)-(self.w//6))//2, self.h//18),
            alpha=0.0
        )
        self.midi_ok_x, self.midi_ok_y = self.midi_window_ok_button.pos
        self.midi_ok_w, self.midi_ok_h = self.midi_window_ok_button.size
        
        self.midi_window_cancel_button = Cv2Button(
            label="cancel",
            pos=((self.w-self.w//2) + ((self.w//2)-(self.w//6))//2, self.h//2),
            size=(((self.w//2)-(self.w//6))//2, self.h//18),
            alpha=0.0
        )
        self.midi_cancel_x, self.midi_cancel_y = self.midi_window_cancel_button.pos
        self.midi_cancel_w, self.midi_cancel_h = self.midi_window_cancel_button.size
    
    def _init_wave_ui(self):
        """UI elementy"""
        # przycisk Wave
        self.wave_button = Cv2Button(
            label="wave", 
            pos=(self.w-(self.w//6), self.h//3), 
            size=(self.w//6, self.h//6), 
            alpha=0.6
        )
        self.wave_x, self.wave_y = self.wave_button.pos
        self.wave_size_w, self.wave_size_h = self.wave_button.size
        
        # okienko ustanien
        self.wave_settings_button = Cv2Button(
            label="",
            pos=(self.w-2*self.w//5, 0),
            size=((2*self.w//5)-(self.w//6), self.h - self.h//4),
            alpha=0
        )
        
        # podkomponenty fali
        self._init_adsr_ui()
        self._init_wave_type_ui()

        self._init_adsr_ui()
        self._init_wave_type_ui()
        self._init_pitch_ui()
        
        # dodatkowe przyciski fali(nie wszystkie narazie są używane, ale będą odrysowane po napisaniu logiki pozniej)
        self.wave_settings_gain_button = Cv2Button(
            label="Gain",
            pos=(self.w-self.w//2, ((self.h - self.h//4)//7)*3),
            size=((self.w//2)-(self.w//6), (self.h - self.h//4)//7),
            alpha=0.6
        )
        self.wave_settings_unison_button = Cv2Button(
            label="Unison",
            pos=(self.w-self.w//2, ((self.h - self.h//4)//7)*4),
            size=((self.w//2)-(self.w//6), (self.h - self.h//4)//7),
            alpha=0.6
        )
        self.wave_settings_wave_morph_button = Cv2Button(
            label="Morph",
            pos=(self.w-self.w//2, ((self.h - self.h//4)//7)*5),
            size=((self.w//2)-(self.w//6), (self.h - self.h//4)//7),
            alpha=0.6
        )
        self.wave_settings_noise_button = Cv2Button(
            label="noise",
            pos=(self.w-self.w//2, ((self.h - self.h//4)//7)*6),
            size=((self.w//2)-(self.w//6), (self.h - self.h//4)//7),
            alpha=0.6
        )

    
    def _init_adsr_ui(self):
        # przycisk ADSR
        self.wave_settings_adsr_button = Cv2Button(
            label="     ADSR     ",
            pos=(self.w-2*self.w//5, (self.h - self.h//4)//7),
            size=((2*self.w//5)-(self.w//6), (self.h - self.h//4)//7),
            alpha=0
        )
        self.wave_adsr_x, self.wave_adsr_y = self.wave_settings_adsr_button.pos
        self.wave_adsr_size_w, self.wave_adsr_size_h = self.wave_settings_adsr_button.size
        
        # okienki ADSR
        self.wave_settings_adsr_window_button = Cv2Button(
            label="",
            pos=(self.w - 4*self.w//5 + self.w//6, 0),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)*4),
            alpha=0
        )
        
        # przycisk Attack
        self.wave_settings_adsr_attack_button = Cv2Button(
            label="     attack     ",
            text_align="top",
            pos=(self.w - 4*self.w//5 + self.w//6, 0),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        
        # przycisk Reset ADSR
        self.wave_settings_adsr_reset_button = Cv2Button(
            label="reset",
            pos=((self.w - 4*self.w//5 + self.w//6) - ((2*self.w//5)-(self.w//6))//2, 0),
            size=(((2*self.w//5)-(self.w//6))//2, ((self.h - self.h//4)//14)),
            alpha=0
        )
        self.wave_adsr_reset_x, self.wave_adsr_reset_y = self.wave_settings_adsr_reset_button.pos
        self.wave_adsr_reset_w, self.wave_adsr_reset_h = self.wave_settings_adsr_reset_button.size
        
        # slider ADSR
        btn_adsr_x = self.w - 4*self.w//5 + self.w//6
        btn_adsr_w = (2*self.w//5) - (self.w//6)
        btn_adsr_h = (self.h - self.h//4)//7
        
        slider_adsr_w = int(btn_adsr_w * 0.6)
        slider_adsr_h = btn_adsr_h
        slider_adsr_x = btn_adsr_x + (btn_adsr_w - slider_adsr_w)//2
        
        self.slider = Cv2Slider(
            pos=(slider_adsr_x, ((self.h - self.h//4)//14) - ((self.h - self.h//4)//28)),
            size=(slider_adsr_w, slider_adsr_h),
            font_scale=0.3,
            font_thickness=1,
            font_color=(0, 0, 0),
            min_val=0,
            max_val=5,
            value=0.01,
            unit="s",
            nonlinear_factor=0.6,
            precision_switch=1,
            visible=False,
            circle_color=(50, 50, 50)
        )
        
        # przycisk Release
        self.wave_settings_adsr_release_button = Cv2Button(
            label="     release     ",
            text_align="top",
            pos=(self.w - 4*self.w//5 + self.w//6, ((self.h - self.h//4)//7)*3),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        
        # slider Release
        btn_release_adsr_x = self.w - 4*self.w//5 + self.w//6
        btn_release_adsr_y = ((self.h - self.h//4)//7)*3
        btn_release_adsr_w = (2*self.w//5) - (self.w//6)
        btn_release_adsr_h = (self.h - self.h//4)//7
        
        slider_release_adsr_w = int(btn_release_adsr_w * 0.6)
        slider_release_adsr_h = btn_release_adsr_h
        slider_release_adsr_x = btn_release_adsr_x + (btn_release_adsr_w - slider_release_adsr_w)//2
        
        self.slider_release = Cv2Slider(
            pos=(slider_release_adsr_x, ((self.h - self.h//4)//14)*7 - ((self.h - self.h//4)//28)),
            size=(slider_release_adsr_w, slider_release_adsr_h),
            font_scale=0.3,
            font_thickness=1,
            font_color=(0, 0, 0),
            min_val=0.01,
            max_val=5,
            value=0.2,
            unit="s",
            nonlinear_factor=0.6,
            precision_switch=1,
            visible=False,
            circle_color=(50, 50, 50)
        )
        
        # przycisk Decay
        self.wave_settings_adsr_decay_button = Cv2Button(
            label="     decay     ",
            text_align="top",
            pos=(self.w - 4*self.w//5 + self.w//6, ((self.h - self.h//4)//7)),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        
        # slider Decay
        btn_decay_adsr_x = self.w - 4*self.w//5 + self.w//6
        btn_decay_adsr_y = ((self.h - self.h//4)//7)
        btn_decay_adsr_w = (2*self.w//5) - (self.w//6)
        btn_decay_adsr_h = (self.h - self.h//4)//7
        
        slider_decay_adsr_w = int(btn_decay_adsr_w * 0.6)
        slider_decay_adsr_h = btn_decay_adsr_h
        slider_decay_adsr_x = btn_decay_adsr_x + (btn_decay_adsr_w - slider_decay_adsr_w)//2
        
        self.slider_decay = Cv2Slider(
            pos=(slider_decay_adsr_x, ((self.h - self.h//4)//14)*3 - ((self.h - self.h//4)//28)),
            size=(slider_decay_adsr_w, slider_decay_adsr_h),
            font_scale=0.3,
            font_thickness=1,
            font_color=(0, 0, 0),
            min_val=0.01,
            max_val=5,
            value=0.05,
            unit="s",
            nonlinear_factor=0.6,
            precision_switch=1,
            visible=False,
            circle_color=(50, 50, 50)
        )
        
        # przycisk Sustain
        self.wave_settings_adsr_sustain_button = Cv2Button(
            label="     sustain     ",
            text_align="top",
            pos=(self.w - 4*self.w//5 + self.w//6, (((self.h - self.h//4)//7))*2),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        
        # slider Sustain
        btn_sustain_adsr_x = self.w - 4*self.w//5 + self.w//6
        btn_sustain_adsr_y = ((self.h - self.h//4)//7)*2
        btn_sustain_adsr_w = (2*self.w//5) - (self.w//6)
        btn_sustain_adsr_h = (self.h - self.h//4)//7
        
        slider_sustain_adsr_w = int(btn_sustain_adsr_w * 0.6)
        slider_sustain_adsr_h = btn_sustain_adsr_h
        slider_sustain_adsr_x = btn_sustain_adsr_x + (btn_sustain_adsr_w - slider_sustain_adsr_w)//2
        
        self.slider_sustain = Cv2Slider(
            pos=(slider_sustain_adsr_x, ((self.h - self.h//4)//14)*5 - ((self.h - self.h//4)//28)),
            size=(slider_sustain_adsr_w, slider_sustain_adsr_h),
            font_scale=0.3,
            font_thickness=1,
            font_color=(0, 0, 0),
            min_val=0.01,
            max_val=1,
            value=0.7,
            unit="",
            nonlinear_factor=0.5,
            visible=False,
            circle_color=(50, 50, 50)
        )
        self.slider_adsr_x = slider_adsr_x
        self.slider_adsr_w = slider_adsr_w
        self.slider_release_adsr_x = slider_release_adsr_x
        self.slider_release_adsr_w = slider_release_adsr_w
        self.slider_decay_adsr_x = slider_decay_adsr_x
        self.slider_decay_adsr_w = slider_decay_adsr_w
        self.slider_sustain_adsr_x = slider_sustain_adsr_x
        self.slider_sustain_adsr_w = slider_sustain_adsr_w

    def _init_wave_type_ui(self):
        """ UI wave"""
        # przycisk Wave Type
        self.wave_settings_wave_type_button = Cv2Button(
            label="Wave type",
            pos=(self.w-2*self.w//5, ((self.h - self.h//4)//7)*2),
            size=((2*self.w//5)-(self.w//6), (self.h - self.h//4)//7),
            alpha=0
        )
        self.wave_type_x, self.wave_type_y = self.wave_settings_wave_type_button.pos
        self.wave_type_size_w, self.wave_type_size_h = self.wave_settings_wave_type_button.size
        
        # przycisk Sine
        self.wave_settings_wave_type_sine_button = Cv2Button(
            label="     Sine     ",
            pos=(self.w - 4*self.w//5 + self.w//6, 0),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        self.wave_type_sine_x, self.wave_type_sine_y = self.wave_settings_wave_type_sine_button.pos
        self.wave_type_sine_size_w, self.wave_type_sine_size_h = self.wave_settings_wave_type_sine_button.size
        
        # przycisk Square
        self.wave_settings_wave_type_squere_button = Cv2Button(
            label="     Squere     ",
            text_align="mid",
            pos=(self.w - 4*self.w//5 + self.w//6, ((self.h - self.h//4)//7)),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        self.wave_type_squere_x, self.wave_type_squere_y = self.wave_settings_wave_type_squere_button.pos
        self.wave_type_squere_size_w, self.wave_type_squere_size_h = self.wave_settings_wave_type_squere_button.size
        
        # slider Pulse Width dla Square
        btn_squere_x = self.w - 4*self.w//5 + self.w//6
        btn_squere_y = (self.h - self.h//4)//7
        btn_squere_w = (2*self.w//5) - (self.w//6)
        btn_squere_h = (self.h - self.h//4)//7
        
        slider_pw_w = int(btn_squere_w * 0.6)
        slider_pw_h = btn_squere_h
        slider_pw_x = btn_squere_x + (btn_squere_w - slider_pw_w)//2
        
        self.slider_pw = Cv2Slider(
            pos=(slider_pw_x, ((self.h - self.h//4)//14)*3 - ((self.h - self.h//4)//28)),
            size=(slider_pw_w, slider_pw_h),
            font_scale=0.3,
            font_thickness=1,
            font_color=(0, 0, 0),
            min_val=1,
            max_val=99,
            value=50,
            unit="%",
            nonlinear_factor=0,
            visible=False,
            circle_color=(50, 50, 50)
        )
        
        # przycisk Saw
        self.wave_settings_wave_type_saw_button = Cv2Button(
            label="     Saw     ",
            pos=(self.w - 4*self.w//5 + self.w//6, ((self.h - self.h//4)//7)*2),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        self.wave_type_saw_x, self.wave_type_saw_y = self.wave_settings_wave_type_saw_button.pos
        self.wave_type_saw_size_w, self.wave_type_saw_size_h = self.wave_settings_wave_type_saw_button.size
        
        # przycisk Triangle
        self.wave_settings_wave_type_tringle_button = Cv2Button(
            label="     Tringle     ",
            pos=(self.w - 4*self.w//5 + self.w//6, ((self.h - self.h//4)//7*3)),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        self.wave_type_tringle_x, self.wave_type_tringle_y = self.wave_settings_wave_type_tringle_button.pos
        self.wave_type_tringle_size_w, self.wave_type_tringle_size_h = self.wave_settings_wave_type_tringle_button.size
        
        # przycisk Hand Control
        self.wave_settings_wave_type_hand_control_button = Cv2Button(
            label="    Hand control    ",
            pos=(self.w - 4*self.w//5 + self.w//6, ((self.h - self.h//4)//7*4)),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        self.wave_type_hand_control_x, self.wave_type_hand_control_y = self.wave_settings_wave_type_hand_control_button.pos
        self.wave_type_hand_control_size_w, self.wave_type_hand_control_size_h = self.wave_settings_wave_type_hand_control_button.size
        
        # okienko dla ustawienia fali za pomoca reki
        self.wave_settings_wave_type_hand_control_window_button = Cv2Button(
            label="put ypur hand here and hold", 
            pos=(self.w-(self.w//3), 0), 
            size=(self.w//3, self.h//3), 
            alpha=0
        )
        self.wave_type_hand_control_set_window_x, self.wave_type_hand_control_set_window_y = self.wave_settings_wave_type_hand_control_window_button.pos
        self.wave_type_hand_control_window_set_size_w, self.wave_type_hand_control_window_set_size_h = self.wave_settings_wave_type_hand_control_window_button.size
    
        self.wave_settings_wave_type_window_button = Cv2Button(
            label="",
            pos=(self.w - 4*self.w//5 + self.w//6, 0),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)*5),
            alpha=0
        )

        self.slider_pw_x = slider_pw_x
        self.slider_pw_w = slider_pw_w


    def _init_pitch_ui(self):
        """UI Pitch"""
        # przycisk Pitch
        self.wave_settings_pitch_button = Cv2Button(
            label="   Pitch   ",
            pos=(self.w-2*self.w//5, ((self.h - self.h//4)//7)*3),
            size=((2*self.w//5)-(self.w//6), (self.h - self.h//4)//7),
            alpha=0
        )
        self.pitch_x, self.pitch_y = self.wave_settings_pitch_button.pos
        self.pitch_size_w, self.pitch_size_h = self.wave_settings_pitch_button.size
        
        # okienko Pitch
        self.wave_settings_pitch_window_button = Cv2Button(
            label="",
            pos=(self.w - 4*self.w//5 + self.w//6, 0),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)*8),
            alpha=0
        )
        
        # przycisk Semitones
        self.wave_settings_pitch_window_semitones_button = Cv2Button(
            label="    Semitones    ",
            text_align="top",
            pos=(self.w - 4*self.w//5 + self.w//6, ((self.h - self.h//4)//7)),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        
        # licznik Semitones
        self.semitones_counter = Cv2Counter(
            pos=((self.w - 4*self.w//5 + self.w//6)+((2*self.w//5)-(self.w//6))//2 - ((2*self.w//5)-(self.w//6))//4, 
                 (((self.h - self.h//4)//7)*2 - ((self.h - self.h//4)//7)//2)),
            size=(((2*self.w//5)-(self.w//6))//2, ((self.h - self.h//4)//7)//3),
            value=0,
            min_val=-12,
            max_val=12,
            alpha=0
        )
        
        self.semitones_counter_x, self.semitones_counter_y = self.semitones_counter.pos
        self.semitones_counter_w, self.semitones_counter_h = self.semitones_counter.size
        
        # przyciski +/- Semitones
        self.semitones_counter_btn_w = self.semitones_counter_w // 4
        self.semitones_counter_minus_x = self.semitones_counter_x
        self.semitones_counter_minus_y = self.semitones_counter_y
        self.semitones_counter_minus_w = self.semitones_counter_btn_w
        self.semitones_counter_minus_h = self.semitones_counter_h
        self.semitones_counter_plus_x = self.semitones_counter_x + self.semitones_counter_w - self.semitones_counter_btn_w
        self.semitones_counter_plus_y = self.semitones_counter_y
        self.semitones_counter_plus_w = self.semitones_counter_btn_w
        self.semitones_counter_plus_h = self.semitones_counter_h
        
        # przycisk Octave
        self.wave_settings_pitch_window_octave_button = Cv2Button(
            label="    Octave    ",
            text_align="top",
            pos=(self.w - 4*self.w//5 + self.w//6, 0),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        
        # licznik Octave
        self.octave_counter = Cv2Counter(
            pos=((self.w - 4*self.w//5 + self.w//6)+((2*self.w//5)-(self.w//6))//2 - ((2*self.w//5)-(self.w//6))//4, 
                 (((self.h - self.h//4)//7) - ((self.h - self.h//4)//7)//2)),
            size=(((2*self.w//5)-(self.w//6))//2, ((self.h - self.h//4)//7)//3),
            value=0,
            min_val=-3,
            max_val=3,
            alpha=0
        )
        
        self.octave_counter_x, self.octave_counter_y = self.octave_counter.pos
        self.octave_counter_w, self.octave_counter_h = self.octave_counter.size
        
        # przyciski +/- Octave
        self.octave_counter_btn_w = self.octave_counter_w // 4
        self.octave_counter_minus_x = self.octave_counter_x
        self.octave_counter_minus_y = self.octave_counter_y
        self.octave_counter_minus_w = self.octave_counter_btn_w
        self.octave_counter_minus_h = self.octave_counter_h
        self.octave_counter_plus_x = self.octave_counter_x + self.octave_counter_w - self.octave_counter_btn_w
        self.octave_counter_plus_y = self.octave_counter_y
        self.octave_counter_plus_w = self.octave_counter_btn_w
        self.octave_counter_plus_h = self.octave_counter_h
        
        # przycisk Cents
        self.wave_settings_pitch_cents_button = Cv2Button(
            label="     Cents     ",
            text_align="top",
            pos=(self.w - 4*self.w//5 + self.w//6, (((self.h - self.h//4)//7))*2),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        
        # slider Cents
        btn_cents_x = self.w - 4*self.w//5 + self.w//6
        btn_cents_y = ((self.h - self.h//4)//7)*2
        btn_cents_w = (2*self.w//5) - (self.w//6)
        btn_cents_h = (self.h - self.h//4)//7
        
        slider_cents_w = int(btn_cents_w * 0.6)
        slider_cents_h = btn_cents_h
        slider_cents_x = btn_cents_x + (btn_cents_w - slider_cents_w)//2
        slider_cents_y = btn_cents_y
        
        self.slider_cents = Cv2Slider(
            pos=(slider_cents_x, ((self.h - self.h//4)//14)*5 - ((self.h - self.h//4)//28)),
            size=(slider_cents_w, slider_cents_h),
            font_scale=0.3,
            font_thickness=1,
            font_color=(0, 0, 0),
            min_val=-100,
            max_val=100,
            value=0,
            unit="",
            visible=False,
            circle_color=(50, 50, 50),
            step=1,
            nonlinear_factor=0
        )
        
        # przycisk Reset Cents
        self.wave_settings_pitch_cents_reset_button = Cv2Button(
            label="reset",
            pos=(self.w - 4*self.w//5 + self.w//6, (((self.h - self.h//4)//7))*2),
            size=((((2*self.w//5)-(self.w//6))//7)*2, (((self.h - self.h//4)//7))//3),
            alpha=0,
            thickness=1
        )
        self.cents_reset_x, self.cents_reset_y = self.wave_settings_pitch_cents_reset_button.pos
        self.cents_reset_w, self.cents_reset_h = self.wave_settings_pitch_cents_reset_button.size
        
        # przycisk Mono
        self.wave_settings_pitch_mono_button = Cv2Button(
            label="    Mono    ",
            text_align="top",
            pos=(self.w - 4*self.w//5 + self.w//6, (((self.h - self.h//4)//7))*3),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        
        # przelacznik(lub po angielsku toggle, dalej dla wygodnosci moge uzywac obaj warianty) Mono
        self.mono_toggle = Cv2Toggle(
            pos=((self.w - 4*self.w//5 + self.w//6)+((2*self.w//5)-(self.w//6))//2 - ((2*self.w//5)-(self.w//6))//4, 
                 (((self.h - self.h//4)//7)*4 - ((self.h - self.h//4)//7)//2)),
            size=(((2*self.w//5)-(self.w//6))//2, ((self.h - self.h//4)//7)//3),
            label="",
            state=False,
            alpha=0
        )
        self.mono_toggle_x, self.mono_toggle_y = self.mono_toggle.pos
        self.mono_toggle_w, self.mono_toggle_h = self.mono_toggle.size
        
        # przycisk Legato
        self.wave_settings_pitch_legato_button = Cv2Button(
            label="   Legato   ",
            text_align="top",
            pos=(self.w - 4*self.w//5 + self.w//6, (((self.h - self.h//4)//7))*4),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        
        # toggle Legato
        self.legato_toggle = Cv2Toggle(
            pos=((self.w - 4*self.w//5 + self.w//6)+((2*self.w//5)-(self.w//6))//2 - ((2*self.w//5)-(self.w//6))//4, 
                 (((self.h - self.h//4)//7)*5 - ((self.h - self.h//4)//7)//2)),
            size=(((2*self.w//5)-(self.w//6))//2, ((self.h - self.h//4)//7)//3),
            label="",
            state=False,
            alpha=0
        )
        self.legato_toggle_x, self.legato_toggle_y = self.legato_toggle.pos
        self.legato_toggle_w, self.legato_toggle_h = self.legato_toggle.size
        
        # przycisk Poly Glide
        self.wave_settings_pitch_poly_glide_button = Cv2Button(
            label="  Poly glide  ",
            text_align="top",
            pos=(self.w - 4*self.w//5 + self.w//6, (((self.h - self.h//4)//7))*5),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        
        # toggle Poly Glide
        self.poly_glide_toggle = Cv2Toggle(
            pos=((self.w - 4*self.w//5 + self.w//6)+((2*self.w//5)-(self.w//6))//2 - ((2*self.w//5)-(self.w//6))//4, 
                 (((self.h - self.h//4)//7)*6 - ((self.h - self.h//4)//7)//2)),
            size=(((2*self.w//5)-(self.w//6))//2, ((self.h - self.h//4)//7)//3),
            label="",
            state=False,
            alpha=0
        )
        self.poly_glide_toggle_x, self.poly_glide_toggle_y = self.poly_glide_toggle.pos
        self.poly_glide_toggle_w, self.poly_glide_toggle_h = self.poly_glide_toggle.size
        
        # przycisk Glide Mode
        self.wave_settings_pitch_glide_mode_button = Cv2Button(
            label="  Glide mode  ",
            text_align="top",
            pos=(self.w - 4*self.w//5 + self.w//6, (((self.h - self.h//4)//7))*6),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)//2),
            alpha=0
        )
        
        # tryby Glide
        self.wave_settings_pitch_glide_mode_legato_button = Cv2Button(
            label="Legato",
            pos=(self.w - 4*self.w//5 + self.w//6, (((self.h - self.h//4)//7))*7 - (((self.h - self.h//4)//7))//2),
            size=(((2*self.w//5)-(self.w//6))//2, (((self.h - self.h//4)//7))//2),
            alpha=0
        )
        self.glide_mode_legato_x, self.glide_mode_legato_y = self.wave_settings_pitch_glide_mode_legato_button.pos
        self.glide_mode_legato_w, self.glide_mode_legato_h = self.wave_settings_pitch_glide_mode_legato_button.size
        
        self.wave_settings_pitch_glide_mode_always_button = Cv2Button(
            label="Always",
            pos=(self.w - 4*self.w//5 + self.w//6 + ((2*self.w//5)-(self.w//6))//2, 
                 (((self.h - self.h//4)//7))*7 - (((self.h - self.h//4)//7))//2),
            size=(((2*self.w//5)-(self.w//6))//2, (((self.h - self.h//4)//7))//2),
            alpha=0
        )
        self.glide_mode_always_x, self.glide_mode_always_y = self.wave_settings_pitch_glide_mode_always_button.pos
        self.glide_mode_always_w, self.glide_mode_always_h = self.wave_settings_pitch_glide_mode_always_button.size
        
        # przycisk Glide Time
        self.wave_settings_pitch_glide_time_button = Cv2Button(
            label="   Glide time   ",
            text_align="top",
            pos=(self.w - 4*self.w//5 + self.w//6, (((self.h - self.h//4)//7))*7),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        
        # slider Glide Time
        btn_gt_x = self.w - 4*self.w//5 + self.w//6
        btn_gt_y = ((self.h - self.h//4)//7)*7
        btn_gt_w = (2*self.w//5) - (self.w//6)
        btn_gt_h = (self.h - self.h//4)//7
        
        slider_gt_w = int(btn_gt_w * 0.6)
        slider_gt_h = btn_gt_h
        slider_gt_x = btn_gt_x + (btn_gt_w - slider_gt_w)//2
        slider_gt_y = btn_gt_y
        
        self.slider_glide_time = Cv2Slider(
            pos=(slider_gt_x, slider_gt_y + ((self.h - self.h//4)//28)),
            size=(slider_gt_w, btn_gt_h),
            font_scale=0.3,
            font_thickness=1,
            font_color=(0, 0, 0),
            min_val=0.01,
            max_val=4,
            value=0.15,
            unit="s",
            visible=False,
            circle_color=(255, 0, 0),
            nonlinear_factor=0.5
        )
        
        # przycisk Phase
        self.wave_settings_pitch_phase_button = Cv2Button(
            label="    Phase    ",
            text_align="top",
            pos=(self.w - 4*self.w//5 + self.w//6, (((self.h - self.h//4)//7))*8),
            size=((2*self.w//5)-(self.w//6), ((self.h - self.h//4)//7)),
            alpha=0
        )
        
        # slider Phase
        btn_phase_x = self.w - 4*self.w//5 + self.w//6
        btn_phase_y = ((self.h - self.h//4)//7)*7
        btn_phase_w = (2*self.w//5) - (self.w//6)
        btn_phase_h = (self.h - self.h//4)//7
        
        slider_phase_w = int(btn_phase_w * 0.6)
        slider_phase_h = btn_phase_h
        slider_phase_x = btn_phase_x + (btn_phase_w - slider_phase_w)//2
        slider_phase_y = btn_phase_y + (self.h - self.h//4)//7 + ((self.h - self.h//4)//28)
        
        self.slider_phase = Cv2Slider(
            pos=(slider_phase_x, slider_phase_y),
            size=(slider_phase_w, btn_phase_h),
            font_scale=0.3,
            font_thickness=1,
            font_color=(0, 0, 0),
            min_val=0,
            max_val=100,
            value=0,
            unit="%",
            visible=False,
            circle_color=(255, 0, 0),
            nonlinear_factor=0
        )
        
        # przycisk Random Phase
        self.wave_settings_pitch_phase_random_button = Cv2Button(
            label="random",
            pos=(self.w - 4*self.w//5 + self.w//6, (((self.h - self.h//4)//7))*8),
            size=((((2*self.w//5)-(self.w//6))//7)*2, (((self.h - self.h//4)//7))//3),
            alpha=0,
            thickness=1
        )
        self.phase_random_x, self.phase_random_y = self.wave_settings_pitch_phase_random_button.pos
        self.phase_random_w, self.phase_random_h = self.wave_settings_pitch_phase_random_button.size        

        self.slider_cents_x = slider_cents_x
        self.slider_cents_w = slider_cents_w
        self.slider_phase_x = slider_phase_x
        self.slider_phase_w = slider_phase_w
        self.slider_phase_y = slider_phase_y
        self.slider_phase_h = slider_phase_h
        self.slider_gt_x = slider_gt_x
        self.slider_gt_w = slider_gt_w

    def load_midi(self, file_path):
        # definicja trybu
        current_mode = "sine"
        if self.squere: 
            current_mode = "square"
        elif self.saw: 
            current_mode = "saw"
        elif self.tringle: 
            current_mode = "triangle"
        elif self.hand: 
            current_mode = "hand"

        if self.player is not None:
            self.player.stop()
        
        # tworzymy player z wybranym trybem
        self.player = MidiPlayer(file_path, server=self.s, wave_type=current_mode)
        
        # jesli tryb hand to fala rysuje sie reka
        if current_mode == "hand":
            self.player.update_table(self.current_hand_points)
        


    def _init_final_states(self):
        # stany przyciskow
        self.play_state = "play"
        self.midi_state = "off"
        self.wave_state = "off"
        self.adsr_state = "off"
        self.wave_type_state = "off"
        self.pitch_state = "off"
        self.glide_mode_always_state = "off"
        self.glide_mode_legato_state = "on"
        self.phase_random_state = "off"
        
        # treking rak
        self.last_fingers_pos = None  
        self.still_timer = None       
        self.fingers_are_still = False 
        
        # punkty domyslne
        self.current_hand_points = [(0, 0.0), (1023, 0.0)]
        
        # stany fal
        self.sine = True
        self.squere = False
        self.saw = False
        self.tringle = False
        self.hand = False
        self.hand_control = False
        
        self.active_button = None
        self.hand_wave = False
        self.hold_duration = 1

    def update_player_params(self):
        if self.player is None:
            return

        semitones_val = getattr(self, "semitones_counter", None)
        octave_val = getattr(self, "octave_counter", None)
        cents_slider = getattr(self, "slider_cents", None)

        coarse = 0
        if semitones_val is not None:
            coarse = semitones_val.value
        if octave_val is not None:
            coarse += octave_val.value * 12

        self.player.coarse = coarse
        self.player.fine = cents_slider.value if cents_slider is not None else 0

        # toggles
        mono_state = getattr(self, "mono_toggle", None)
        legato_state = getattr(self, "legato_toggle", None)
        poly_glide_state = getattr(self, "poly_glide_toggle", None)

        if mono_state is not None:
            try:
                self.player.set_mono(mono_state.state)
            except Exception:
                pass
        if legato_state is not None:
            try:
                self.player.set_legato(legato_state.state)
            except Exception:
                pass
        if poly_glide_state is not None:
            try:
                self.player.set_poly_portamento(poly_glide_state.state)
            except Exception:
                pass

        # Glide / Portamento logic
        glide_slider = getattr(self, "slider_glide_time", None)
        glide_val = glide_slider.value if glide_slider is not None else 0.0

        try:
            if poly_glide_state is not None and poly_glide_state.state:

                if getattr(self, "glide_mode_legato_state", "on") == "on":
                    self.player.set_portamento(0, "legato")
                else:
                    self.player.set_portamento(glide_val, "always")
            else:
                if getattr(self, "glide_mode_legato_state", "on") == "on":
                    self.player.set_portamento(glide_val, "legato")
                else:
                    self.player.set_portamento(glide_val, "always")
        except Exception:
            pass

        # Phase / random phase
        try:
            if getattr(self, "phase_random_state", "off") == "on":
                self.player.set_random_phase(True)
                if hasattr(self.player, "get_current_phase_value") and hasattr(self, "slider_phase"):
                    self.slider_phase.value = self.player.get_current_phase_value() * 100
            else:
                self.player.set_random_phase(False)
                if hasattr(self, "slider_phase"):
                    self.player.set_phase(self.slider_phase.value / 100)
        except Exception:
            pass

    def process_hand_gesture(self, result, img):
        """
        opracowanie gestow rak.
        ta metoda musi sie wylowywac po otrzymaniu wyniku od HandProcessor.

        Args:
            result: wynik opracowania hendprocessor
            img: kadr wideo ktory teraz
        """
        if result is None:
            return

        try:
            wave_points, rect, index_finger, all_fingers = result
        except Exception:
            # ignorowanie kadru jesli jakis z wnikow nie otrzymany(najczesciej to jest przy odpalaniu funkcji dpoero a na nastepnym kadrze jest juz okej)
            return

        x1, y1, x2, y2 = rect if rect is not None else (0, 0, 0, 0)
        ix, iy = index_finger if index_finger is not None else (0, 0)

        self.process_midi_window(ix, iy, all_fingers)

        # nowa pozycja palcow - nowa fala
        if wave_points is not None:
            self.update_hand_wave(wave_points)

        # update ADSR
        self.update_adsr_params()

        if all_fingers and isinstance(all_fingers, (list, tuple)) and len(all_fingers) >= 5:
            try:
                thumb_x, thumb_y = all_fingers[0]
                index_x, index_y = all_fingers[1]
                middle_x, middle_y = all_fingers[2]
                ring_x, ring_y = all_fingers[3]
                pinky_x, pinky_y = all_fingers[4]
            except Exception:
                pass
            
            if not self.hand_control:
                # sprawdzenie czy palec jest w zonie przycisku
                in_play_button_zone = (self.play_x <= ix <= self.play_x + self.play_size_w and 
                                       self.play_y <= iy <= self.play_y + self.play_size_h)
                in_midi_button_zone = (self.midi_x <= ix <= self.midi_x + self.midi_size_w and 
                                       self.midi_y <= iy <= self.midi_y + self.midi_size_h)
                in_wave_button_zone = (self.wave_x <= ix <= self.wave_x + self.wave_size_w and 
                                       self.wave_y <= iy <= self.wave_y + self.wave_size_h)
            else:
                in_play_button_zone = False
                in_midi_button_zone = False
                in_wave_button_zone = False
            
            in_midi_button_down_zone = (self.midi_down_x <= ix <= self.midi_down_x + self.midi_size_down_w and 
                                        self.midi_down_y <= iy <= self.midi_down_y + self.midi_size_down_h)
            in_midi_button_up_zone = (self.midi_up_x <= ix <= self.midi_up_x + self.midi_size_up_w and 
                                      self.midi_up_y <= iy <= self.midi_up_y + self.midi_size_up_h)
            in_midi_button_ok_zone = (self.midi_ok_x <= ix <= self.midi_ok_x + self.midi_ok_w and 
                                      self.midi_ok_y <= iy <= self.midi_ok_y + self.midi_ok_h)
            in_wave_adsr_reset_zone = (self.wave_adsr_reset_x <= ix <= self.wave_adsr_reset_x + self.wave_adsr_reset_w and 
                                       self.wave_adsr_reset_y <= iy <= self.wave_adsr_reset_y + self.wave_adsr_reset_h)
            in_midi_button_cancel_zone = (self.midi_cancel_x <= ix <= self.midi_cancel_x + self.midi_cancel_w and 
                                          self.midi_cancel_y <= iy <= self.midi_cancel_y + self.midi_cancel_h)
            in_wave_button_adsr_zone = (self.wave_adsr_x <= ix <= self.wave_adsr_x + self.wave_adsr_size_w and 
                                        self.wave_adsr_y <= iy <= self.wave_adsr_y + self.wave_adsr_size_h)
            in_pitch_button_zone = (self.pitch_x <= ix <= self.pitch_x + self.pitch_size_w and 
                                    self.pitch_y <= iy <= self.pitch_y + self.pitch_size_h)
            
            tolerance = 5  # +- pikseli od linii
            
            cy = self.slider.circle_pos[1]
            cy_rel = self.slider_release.circle_pos[1]
            cy_dec = self.slider_decay.circle_pos[1]
            cy_sus = self.slider_sustain.circle_pos[1]
            cy_pw = self.slider_pw.circle_pos[1]
            cy_cen = self.slider_cents.circle_pos[1]
            cy_gt = self.slider_glide_time.circle_pos[1]
            cy_phase = self.slider_phase_y + self.slider_phase_h // 2

            # zony dla sliderow
            in_slider_zone = (self.slider_adsr_x <= ix <= self.slider_adsr_x + self.slider_adsr_w) and \
                            (cy - tolerance <= iy <= cy + tolerance)
            in_release_slider_zone = (self.slider_release_adsr_x <= ix <= self.slider_release_adsr_x + self.slider_release_adsr_w) and \
                                    (cy_rel - tolerance <= iy <= cy_rel + tolerance)

            in_decay_slider_zone = (self.slider_decay_adsr_x <= ix <= self.slider_decay_adsr_x + self.slider_decay_adsr_w) and \
                                  (cy_dec - tolerance <= iy <= cy_dec + tolerance)
            in_sustain_slider_zone = (self.slider_sustain_adsr_x <= ix <= self.slider_sustain_adsr_x + self.slider_sustain_adsr_w) and \
                                    (cy_sus - tolerance <= iy <= cy_sus + tolerance)
            in_cents_slider_zone = (self.slider_cents_x <= ix <= self.slider_cents_x + self.slider_cents_w) and \
                                  (cy_cen - tolerance <= iy <= cy_cen + tolerance)
            in_phase_slider_zone = (self.slider_phase_x <= ix <= self.slider_phase_x + self.slider_phase_w) and \
                                  (cy_phase - tolerance <= iy <= cy_phase + tolerance)
            in_glide_time_slider_zone = (self.slider_gt_x <= ix <= self.slider_gt_x + self.slider_gt_w) and \
                                       (cy_gt - tolerance <= iy <= cy_gt + tolerance)
            in_pw_slider_zone = (self.slider_pw_x <= ix <= self.slider_pw_x + self.slider_pw_w) and \
                               (cy_pw - tolerance <= iy <= cy_pw + tolerance)
        
            # inne zony (przyciski, toggly itd)
            in_cents_reset_zone = (self.cents_reset_x <= ix <= self.cents_reset_x + self.cents_reset_w and 
                                  self.cents_reset_y <= iy <= self.cents_reset_y + self.cents_reset_h)
            in_phase_random_zone = (self.phase_random_x <= ix <= self.phase_random_x + self.phase_random_w and 
                                   self.phase_random_y <= iy <= self.phase_random_y + self.phase_random_h)
            in_wave_button_type_zone = (self.wave_type_x <= ix <= self.wave_type_x + self.wave_type_size_w and 
                                       self.wave_type_y <= iy <= self.wave_type_y + self.wave_type_size_h)
            in_wave_button_type_sine_zone = (self.wave_type_sine_x <= ix <= self.wave_type_sine_x + self.wave_type_sine_size_w and 
                                            self.wave_type_sine_y <= iy <= self.wave_type_sine_y + self.wave_type_sine_size_h)
            in_wave_button_type_squere_zone = (self.wave_type_squere_x <= ix <= self.wave_type_squere_x + self.wave_type_squere_size_w and 
                                              self.wave_type_squere_y <= iy <= self.wave_type_squere_y + self.wave_type_squere_size_h)
            in_wave_button_type_saw_zone = (self.wave_type_saw_x <= ix <= self.wave_type_saw_x + self.wave_type_saw_size_w and 
                                           self.wave_type_saw_y <= iy <= self.wave_type_saw_y + self.wave_type_saw_size_h)
            in_wave_button_type_tringle_zone = (self.wave_type_tringle_x <= ix <= self.wave_type_tringle_x + self.wave_type_tringle_size_w and 
                                               self.wave_type_tringle_y <= iy <= self.wave_type_tringle_y + self.wave_type_tringle_size_h)
            in_hand_window_zone = (self.wave_type_hand_control_x <= ix <= self.wave_type_hand_control_x + self.wave_type_hand_control_size_w and 
                                  self.wave_type_hand_control_y <= iy <= self.wave_type_hand_control_y + self.wave_type_hand_control_size_h)
            in_semitones_counter_minus_zone = (self.semitones_counter_minus_x <= ix <= self.semitones_counter_minus_x + self.semitones_counter_minus_w and 
                                              self.semitones_counter_minus_y <= iy <= self.semitones_counter_minus_y + self.semitones_counter_minus_h)
            in_semitones_counter_plus_zone = (self.semitones_counter_plus_x <= ix <= self.semitones_counter_plus_x + self.semitones_counter_plus_w and 
                                             self.semitones_counter_plus_y <= iy <= self.semitones_counter_plus_y + self.semitones_counter_plus_h)
            in_octave_counter_minus_zone = (self.octave_counter_minus_x <= ix <= self.octave_counter_minus_x + self.octave_counter_minus_w and 
                                           self.octave_counter_minus_y <= iy <= self.octave_counter_minus_y + self.octave_counter_minus_h)
            in_octave_counter_plus_zone = (self.octave_counter_plus_x <= ix <= self.octave_counter_plus_x + self.octave_counter_plus_w and 
                                          self.octave_counter_plus_y <= iy <= self.octave_counter_plus_y + self.octave_counter_plus_h)
            in_mono_toggle_zone = (self.mono_toggle_x <= ix <= self.mono_toggle_x + self.mono_toggle_w and 
                                  self.mono_toggle_y <= iy <= self.mono_toggle_y + self.mono_toggle_h)
            in_legato_toggle_zone = (self.legato_toggle_x <= ix <= self.legato_toggle_x + self.legato_toggle_w and 
                                    self.legato_toggle_y <= iy <= self.legato_toggle_y + self.legato_toggle_h)
            in_poly_glide_toggle_zone = (self.poly_glide_toggle_x <= ix <= self.poly_glide_toggle_x + self.poly_glide_toggle_w and 
                                        self.poly_glide_toggle_y <= iy <= self.poly_glide_toggle_y + self.poly_glide_toggle_h)
            in_glide_mode_legato_zone = (self.glide_mode_legato_x <= ix <= self.glide_mode_legato_x + self.glide_mode_legato_w and 
                                        self.glide_mode_legato_y <= iy <= self.glide_mode_legato_y + self.glide_mode_legato_h)
            in_glide_mode_always_zone = (self.glide_mode_always_x <= ix <= self.glide_mode_always_x + self.glide_mode_always_w and 
                                        self.glide_mode_always_y <= iy <= self.glide_mode_always_y + self.glide_mode_always_h)

            in_wave_button_type_hand_control_zone = (self.wave_type_hand_control_x <= ix <= self.wave_type_hand_control_x + self.wave_type_hand_control_size_w and
                                                    self.wave_type_hand_control_y <= iy <= self.wave_type_hand_control_y + self.wave_type_hand_control_size_h)

            in_hand_window_set_zone = (

                self.wave_type_hand_control_set_window_x <= thumb_x <= self.wave_type_hand_control_set_window_x + self.wave_type_hand_control_window_set_size_w and \
                self.wave_type_hand_control_set_window_y <= thumb_y <= self.wave_type_hand_control_set_window_y + self.wave_type_hand_control_window_set_size_h and \

                self.wave_type_hand_control_set_window_x <= index_x <= self.wave_type_hand_control_set_window_x + self.wave_type_hand_control_window_set_size_w and \
                self.wave_type_hand_control_set_window_y <= index_y <= self.wave_type_hand_control_set_window_y + self.wave_type_hand_control_window_set_size_h and \

                self.wave_type_hand_control_set_window_x <= middle_x <= self.wave_type_hand_control_set_window_x + self.wave_type_hand_control_window_set_size_w and \
                self.wave_type_hand_control_set_window_y <= middle_y <= self.wave_type_hand_control_set_window_y + self.wave_type_hand_control_window_set_size_h and \

                self.wave_type_hand_control_set_window_x <= ring_x <= self.wave_type_hand_control_set_window_x + self.wave_type_hand_control_window_set_size_w and \
                self.wave_type_hand_control_set_window_y <= ring_y <= self.wave_type_hand_control_set_window_y + self.wave_type_hand_control_window_set_size_h and \

                self.wave_type_hand_control_set_window_x <= pinky_x <= self.wave_type_hand_control_set_window_x + self.wave_type_hand_control_window_set_size_w and \
                self.wave_type_hand_control_set_window_y <= pinky_y <= self.wave_type_hand_control_window_set_size_h
            )
            
            


            # ADSR RESET logika przycisku

            if self.adsr_state == 'on':
                self.wave_settings_adsr_reset_button.alpha = 0.3

                if in_wave_adsr_reset_zone:
                    self.wave_settings_adsr_reset_button.alpha = 0.8

                    if self.timer_adsr_reset is None:
                        self.timer_adsr_reset = time.time()

                    elif time.time() - self.timer_adsr_reset >= 3:

                        self.slider.reset_value(0.01)
                        self.slider_decay.reset_value(0.05)
                        self.slider_sustain.reset_value(0.7)
                        self.slider_release.reset_value(0.2)

                        self.wave_settings_adsr_reset_button.alpha = 0.3
                        self.timer_adsr_reset = None

                else:
                    self.wave_settings_adsr_reset_button.alpha = 0.3
                    self.timer_adsr_reset = None

            else:
                self.wave_settings_adsr_reset_button.alpha = 0
                self.timer_adsr_reset = None

            if self.pitch_state == "on" and in_cents_slider_zone:
                # fiksacja w zonie
                if self.timer_cents_zone is None:
                    self.timer_cents_zone = time.time()
                    self.slider_cents_timer = None
                    self.slider_active = False
                elif time.time() - self.timer_cents_zone >= self.hold_duration:
                    self.slider_active = True

                if self.slider_active:
                    if not getattr(self, "slider_cents_locked", False):
                        w = getattr(self, "slider_cents_w", 0) or 0
                        if w != 0:
                            rel = (ix - getattr(self, "slider_cents_x", 0)) / float(w)
                            rel = max(0.0, min(1.0, rel))
                            v = (self.slider_cents.min_val +
                                rel * (self.slider_cents.max_val - self.slider_cents.min_val))
                            self.slider_cents.value = v

                    # magnet
                    if getattr(self, "slider_cents_timer", None) is None:
                        self.slider_cents_timer = time.time()
                        self.slider_cents_snap_value = self.slider_cents.value
                    else:
                        snap_x = None
                        minv = self.slider_cents.min_val
                        maxv = self.slider_cents.max_val
                        if (maxv - minv) != 0:
                            snap_x = (self.slider_cents_x +
                                    ((self.slider_cents_snap_value - minv) / (maxv - minv)) * self.slider_cents_w)
                        if snap_x is not None and abs(ix - snap_x) <= 3:
                            if time.time() - self.slider_cents_timer >= 2:
                                self.slider_cents.value = self.slider_cents_snap_value
                        else:
                            self.slider_cents_timer = time.time()
                            self.slider_cents_snap_value = self.slider_cents.value

                    # stop jesli nie rusza sie o 8 pixeli
                    if getattr(self, "slider_cents_last_ix", None) is None:
                        self.slider_cents_last_ix = ix
                        self.slider_cents_stop_timer = time.time()
                    elif abs(ix - self.slider_cents_last_ix) <= 8:
                        if time.time() - self.slider_cents_stop_timer >= 1:
                            try:
                                self.slider_cents.circle_color = (0, 200, 200)
                            except Exception:
                                pass
                            self.slider_cents_locked = True
                    else:
                        self.slider_cents_last_ix = ix
                        self.slider_cents_stop_timer = time.time()
                        self.slider_cents_locked = False
                        try:
                            self.slider_cents.circle_color = (50, 50, 50)
                        except Exception:
                            pass

            else:
                # zwracanie stanu z powrotem jesli palec wyszedl
                self.timer_cents_zone = None
                self.slider_cents_timer = None
                self.slider_cents_last_ix = None
                self.slider_cents_stop_timer = None
                self.slider_cents_snap_value = None
                self.slider_cents_locked = False
                self.slider_active = False

            if self.adsr_state == "on" and in_slider_zone:
                if self.timer_adsr_slider is None:
                    self.timer_adsr_slider = time.time()
                elif time.time() - self.timer_adsr_slider >= self.hold_duration:
                    if not self.slider_locked:
                        relative_x = ix - self.slider_adsr_x
                        self.slider.value = max(
                            self.slider.min_val,
                            min(
                                self.slider.max_val,
                                (relative_x / self.slider_adsr_w) * (self.slider.max_val - self.slider.min_val)
                            )
                        )
                    
                    # magnet
                    if self.slider_hold_timer is None:
                        self.slider_hold_timer = time.time()
                        self.slider_snap_value = self.slider.value
                    else:
                        if abs(ix - (self.slider_adsr_x + (self.slider_snap_value / self.slider.max_val) * self.slider_adsr_w)) <= 3:
                            if time.time() - self.slider_hold_timer >= 2:
                                self.slider.value = self.slider_snap_value
                        else:
                            self.slider_hold_timer = time.time()
                            self.slider_snap_value = self.slider.value
                    
                    # stop
                    if self.slider_last_ix is None:
                        self.slider_last_ix = ix
                        self.slider_stop_timer = time.time()
                    elif abs(ix - self.slider_last_ix) <= 8:
                        if time.time() - self.slider_stop_timer >= 1:
                            self.slider.circle_color = (0, 200, 200)
                            self.slider_locked = True
                    else:
                        self.slider_last_ix = ix
                        self.slider_stop_timer = time.time()
                        self.slider_locked = False
                        self.slider.circle_color = (50, 50, 50)
            else:
                self.slider_hold_timer = None
                self.slider_last_ix = None
                self.slider_stop_timer = None
                self.slider_locked = False
                self.timer_adsr_slider = None
                self.slider.circle_color = (50, 50, 50)

            """

            Dalej dla release itd, wsm jak i dla wszystkich przyciskow logika prawie sie nie rozni, kopi past,
            jak bede dorabiac ten project trzeba zrobic osobna klase

            """

            if self.adsr_state == "on" and in_release_slider_zone:
                if self.timer_adsr_slider_hold is None:
                    self.timer_adsr_slider_hold = time.time()
                elif time.time() - self.timer_adsr_slider_hold >= self.hold_duration:
                    if not self.slider_release_locked:
                        relative_x = ix - self.slider_release_adsr_x
                        self.slider_release.value = max(
                            self.slider_release.min_val,
                            min(
                                self.slider_release.max_val,
                                (relative_x / self.slider_release_adsr_w) * (self.slider_release.max_val - self.slider_release.min_val)
                            )
                        )
                    

                    if self.slider_release_hold_timer is None:
                        self.slider_release_hold_timer = time.time()
                        self.slider_release_snap_value = self.slider_release.value
                    else:
                        if abs(ix - (self.slider_release_adsr_x + (self.slider_release_snap_value / self.slider_release.max_val) * self.slider_release_adsr_w)) <= 3:
                            if time.time() - self.slider_release_hold_timer >= 2:
                                self.slider_release.value = self.slider_release_snap_value
                        else:
                            self.slider_release_hold_timer = time.time()
                            self.slider_release_snap_value = self.slider_release.value
                    

                    if self.slider_release_last_ix is None:
                        self.slider_release_last_ix = ix
                        self.slider_release_stop_timer = time.time()
                    elif abs(ix - self.slider_release_last_ix) <= 8:
                        if time.time() - self.slider_release_stop_timer >= 1:
                            self.slider_release.circle_color = (0, 200, 200)
                            self.slider_release_locked = True
                    else:
                        self.slider_release_last_ix = ix
                        self.slider_release_stop_timer = time.time()
                        self.slider_release_locked = False
                        self.slider_release.circle_color = (50, 50, 50)
            else:
                self.slider_release_hold_timer = None
                self.slider_release_last_ix = None
                self.slider_release_stop_timer = None
                self.slider_release_locked = False
                self.timer_adsr_slider_hold = None
                self.slider_release.circle_color = (50, 50, 50)

            #Decay (ADSR)
            if self.adsr_state == "on" and in_decay_slider_zone:
                if self.timer_fixed_ix is None:
                    self.timer_fixed_ix = time.time()
                elif time.time() - self.timer_fixed_ix >= self.hold_duration:
                    if not self.slider_decay_locked:
                        relative_x = ix - self.slider_decay_adsr_x
                        self.slider_decay.value = max(
                            self.slider_decay.min_val,
                            min(
                                self.slider_decay.max_val,
                                (relative_x / self.slider_decay_adsr_w) * (self.slider_decay.max_val - self.slider_decay.min_val)
                            )
                        )
                    

                    if self.slider_decay_hold_timer is None:
                        self.slider_decay_hold_timer = time.time()
                        self.slider_decay_snap_value = self.slider_decay.value
                    else:
                        if abs(ix - (self.slider_decay_adsr_x + (self.slider_decay_snap_value / self.slider_decay.max_val) * self.slider_decay_adsr_w)) <= 3:
                            if time.time() - self.slider_decay_hold_timer >= 2:
                                self.slider_decay.value = self.slider_decay_snap_value
                        else:
                            self.slider_decay_hold_timer = time.time()
                            self.slider_decay_snap_value = self.slider_decay.value
                    

                    if self.slider_decay_last_ix is None:
                        self.slider_decay_last_ix = ix
                        self.slider_decay_stop_timer = time.time()
                    elif abs(ix - self.slider_decay_last_ix) <= 8:
                        if time.time() - self.slider_decay_stop_timer >= 1:
                            self.slider_decay.circle_color = (0, 200, 200)
                            self.slider_decay_locked = True
                    else:
                        self.slider_decay_last_ix = ix
                        self.slider_decay_stop_timer = time.time()
                        self.slider_decay_locked = False
                        self.slider_decay.circle_color = (50, 50, 50)
            else:
                self.slider_decay_hold_timer = None
                self.slider_decay_last_ix = None
                self.slider_decay_stop_timer = None
                self.slider_decay_locked = False
                self.timer_fixed_ix = None
                self.slider_decay.circle_color = (50, 50, 50)

            # Sustain (ADSR)
            if self.adsr_state == "on" and in_sustain_slider_zone:
                if self.timer_slider_sustain_zone is None:
                    self.timer_slider_sustain_zone = time.time()
                elif time.time() - self.timer_slider_sustain_zone >= self.hold_duration:
                    if not self.slider_sustain_locked:
                        relative_x = ix - self.slider_sustain_adsr_x
                        self.slider_sustain.value = max(
                            self.slider_sustain.min_val,
                            min(
                                self.slider_sustain.max_val,
                                (relative_x / self.slider_sustain_adsr_w) * (self.slider_sustain.max_val - self.slider_sustain.min_val)
                            )
                        )
                    

                    if self.slider_sustain_hold_timer is None:
                        self.slider_sustain_hold_timer = time.time()
                        self.slider_sustain_snap_value = self.slider_sustain.value
                    else:
                        if abs(ix - (self.slider_sustain_adsr_x + (self.slider_sustain_snap_value / self.slider_sustain.max_val) * self.slider_sustain_adsr_w)) <= 3:
                            if time.time() - self.slider_sustain_hold_timer >= 2:
                                self.slider_sustain.value = self.slider_sustain_snap_value
                        else:
                            self.slider_sustain_hold_timer = time.time()
                            self.slider_sustain_snap_value = self.slider_sustain.value
                    

                    if self.slider_sustain_last_ix is None:
                        self.slider_sustain_last_ix = ix
                        self.slider_sustain_stop_timer = time.time()
                    elif abs(ix - self.slider_sustain_last_ix) <= 8:
                        if time.time() - self.slider_sustain_stop_timer >= 1:
                            self.slider_sustain.circle_color = (0, 200, 200)
                            self.slider_sustain_locked = True
                    else:
                        self.slider_sustain_last_ix = ix
                        self.slider_sustain_stop_timer = time.time()
                        self.slider_sustain_locked = False
                        self.slider_sustain.circle_color = (50, 50, 50)
            else:
                self.slider_sustain_hold_timer = None
                self.slider_sustain_last_ix = None
                self.slider_sustain_stop_timer = None
                self.slider_sustain_locked = False
                self.timer_slider_sustain_zone = None
                self.slider_sustain.circle_color = (50, 50, 50)
            # Play
            if in_play_button_zone:
                self.play_button.alpha = 0.8
                if self.timer_start is None:
                    self.timer_start = time.time()
                elif time.time() - self.timer_start >= self.hold_duration:
                    if self.play_state == "play":
                        self.play_state = "stop"
                        self.play_button.label = "stop"
                        if self.player is not None:
                            self.player.play()
                    else:
                        self.play_state = "play"
                        self.play_button.label = "play"
                        if self.player is not None:
                            self.player.stop()
                    self.timer_start = None  
            else:
                if not self.hand_control:
                    self.play_button.alpha = 0.6
                self.timer_start = None 
            
            # Wave
            if in_wave_button_zone and self.midi_state == "off":
                self.wave_button.alpha = 0.8
                if self.timer_wave is None:
                    self.timer_wave = time.time()
                elif time.time() - self.timer_wave >= self.hold_duration:
                    if self.wave_state == "off":
                        self.wave_state = "on"
                        self.wave_settings_button.alpha = 0.1
                        self.wave_settings_adsr_button.alpha = 0.6
                    else:
                        self.wave_state = "off"
                        self.adsr_state = "off"
                        self.slider.visible = False
                        self.slider_release.visible = False
                        self.slider_decay.visible = False
                        self.wave_settings_button.alpha = 0
                        self.wave_settings_adsr_button.alpha = 0
                    self.timer_wave = None
            else:
                if not self.hand_control:
                    self.wave_button.alpha = 0.6
                self.timer_wave = None
            
            # Wave
            if self.wave_state == "on":
                self.wave_settings_adsr_button.alpha = 0.6
                
                if in_wave_button_adsr_zone and self.wave_type_state == "off" and self.pitch_state == "off":
                    self.wave_settings_adsr_button.alpha = 0.8
                    if self.timer_adsr is None:
                        self.timer_adsr = time.time()
                    elif time.time() - self.timer_adsr >= self.hold_duration:
                        if self.adsr_state == "off":
                            self.adsr_state = "on"
                            self.slider_release.visible = True
                            self.slider_decay.visible = True
                            self.slider_sustain.visible = True
                            self.slider.visible = True
                            self.wave_settings_adsr_attack_button.alpha = 0.6
                            self.wave_settings_adsr_window_button.alpha = 0.1
                            self.wave_settings_adsr_release_button.alpha = 0.6
                            self.wave_settings_adsr_decay_button.alpha = 0.6
                            self.wave_settings_adsr_sustain_button.alpha = 0.6
                        else:
                            self.slider_release.visible = False
                            self.slider_decay.visible = False
                            self.slider_sustain.visible = False
                            self.slider.visible = False
                            self.adsr_state = "off"
                            self.wave_settings_adsr_release_button.alpha = 0
                            self.wave_settings_adsr_attack_button.alpha = 0
                            self.wave_settings_adsr_window_button.alpha = 0
                            self.wave_settings_adsr_decay_button.alpha = 0
                            self.wave_settings_adsr_sustain_button.alpha = 0
                        self.timer_adsr = None
                else:
                    self.timer_adsr = None
            else:
                self.wave_settings_button.alpha = 0
                self.wave_settings_adsr_button.alpha = 0
                self.wave_settings_adsr_attack_button.alpha = 0
                self.wave_settings_adsr_window_button.alpha = 0
                self.wave_settings_adsr_release_button.alpha = 0
                self.wave_settings_adsr_decay_button.alpha = 0
                self.wave_settings_adsr_sustain_button.alpha = 0
                self.slider.visible = False
                self.slider_release.visible = False
                self.slider_decay.visible = False
                self.slider_sustain.visible = False
                self.timer_adsr = None

        # Wave Type
        if self.wave_state == "on":
            self.wave_settings_wave_type_button.alpha = 0.6

            if in_wave_button_type_zone and self.adsr_state == "off" and self.pitch_state == "off":
                self.wave_settings_wave_type_button.alpha = 0.8
                    
                if self.timer_wave_type is None:
                    self.timer_wave_type = time.time()

                elif time.time() - self.timer_wave_type >= self.hold_duration:
                    if self.wave_type_state == "off":
                        self.wave_type_state = "on"
                        self.timer_wave_type = None
                        self.wave_settings_wave_type_window_button.alpha = 0.1
                        self.wave_settings_wave_type_sine_button.alpha = 0.6
                        self.wave_settings_wave_type_squere_button.alpha = 0.6
                        self.wave_settings_wave_type_saw_button.alpha = 0.6
                        self.wave_settings_wave_type_tringle_button.alpha = 0.6
                        
                    else:
                        self.wave_type_state = "off"
                        self.wave_settings_wave_type_sine_button.alpha = 0
                        self.wave_settings_wave_type_squere_button.alpha = 0
                        self.wave_settings_wave_type_saw_button.alpha = 0
                        self.wave_settings_wave_type_tringle_button.alpha = 0
                        self.timer_wave_type = None
                        self.wave_settings_wave_type_window_button.alpha = 0
            else:          
                self.timer_wave_type = None
                self.wave_settings_wave_type_button.alpha = 0.6
        else:
            self.wave_type_state = "off"            
            self.wave_settings_wave_type_sine_button.alpha = 0
            self.wave_settings_wave_type_squere_button.alpha = 0
            self.wave_settings_wave_type_saw_button.alpha = 0
            self.wave_settings_wave_type_tringle_button.alpha = 0
            self.wave_settings_wave_type_button.alpha = 0
            self.timer_wave_type = None
            self.wave_settings_wave_type_window_button.alpha = 0

        # Pitch
        if self.pitch_state == "on":
            if self.phase_random_state == "off" and not in_phase_random_zone:
                self.wave_settings_pitch_phase_random_button.alpha = 0.6
            elif self.phase_random_state == "off" and in_phase_random_zone:
                self.wave_settings_pitch_phase_random_button.alpha = 0.8
            elif self.phase_random_state == "on":
                self.wave_settings_pitch_phase_random_button.alpha = 1
            elif self.phase_random_state == "on" and in_phase_random_zone:
                self.wave_settings_pitch_phase_random_button.alpha = 0.8

            if not in_cents_reset_zone:
                self.wave_settings_pitch_cents_reset_button.alpha = 0.6
            else:
                self.wave_settings_pitch_cents_reset_button.alpha = 0.8
            self.wave_settings_pitch_glide_time_button.alpha = 0.6
            self.wave_settings_pitch_window_semitones_button.alpha = 0.6
            self.wave_settings_pitch_window_octave_button.alpha = 0.6
            self.wave_settings_pitch_cents_button.alpha = 0.6
            self.wave_settings_pitch_mono_button.alpha = 0.6
            self.wave_settings_pitch_legato_button.alpha = 0.6
            self.wave_settings_pitch_poly_glide_button.alpha = 0.6
            self.wave_settings_pitch_glide_mode_button.alpha = 0.6
            self.wave_settings_pitch_phase_button.alpha = 0.6
            self.mono_toggle.alpha = 0.8
            self.poly_glide_toggle.alpha = 0.8
            self.legato_toggle.alpha = 0.8
            self.slider_cents.visible = True
            self.slider_glide_time.visible = True
            self.slider_phase.visible = True
            if self.glide_mode_legato_state == "off" and not in_glide_mode_legato_zone:
                self.wave_settings_pitch_glide_mode_legato_button.alpha = 0.6
            elif self.glide_mode_legato_state == "off" and in_glide_mode_legato_zone:
                self.wave_settings_pitch_glide_mode_legato_button.alpha = 1
            elif self.glide_mode_legato_state == "on":
                self.wave_settings_pitch_glide_mode_legato_button.alpha = 1
            if self.glide_mode_always_state == "off" and not in_glide_mode_always_zone:
                self.wave_settings_pitch_glide_mode_always_button.alpha = 0.6
            elif self.glide_mode_always_state == "off" and in_glide_mode_always_zone:
                self.wave_settings_pitch_glide_mode_always_button.alpha = 1
            elif self.glide_mode_always_state == "on":
                self.wave_settings_pitch_glide_mode_always_button.alpha = 1   
        else:
            self.wave_settings_pitch_phase_random_button.alpha = 0
            self.wave_settings_pitch_cents_reset_button.alpha = 0
            self.wave_settings_pitch_glide_time_button.alpha = 0
            self.wave_settings_pitch_glide_mode_button.alpha = 0
            self.wave_settings_pitch_window_octave_button.alpha = 0
            self.wave_settings_pitch_window_semitones_button.alpha = 0
            self.wave_settings_pitch_cents_button.alpha = 0
            self.wave_settings_pitch_mono_button.alpha = 0
            self.wave_settings_pitch_legato_button.alpha = 0
            self.wave_settings_pitch_poly_glide_button.alpha = 0
            self.mono_toggle.alpha = 0
            self.legato_toggle.alpha = 0
            self.poly_glide_toggle.alpha = 0
            self.wave_settings_pitch_glide_mode_always_button.alpha = 0
            self.wave_settings_pitch_glide_mode_legato_button.alpha = 0
            self.wave_settings_pitch_phase_button.alpha = 0
            self.slider_cents.visible = False
            self.slider_glide_time.visible = False
            self.slider_phase.visible = False

        # Wave Type
        if self.wave_type_state == "on":
            # SINE
            if not self.sine:
                self.wave_settings_wave_type_sine_button.alpha = 0.6
                if in_wave_button_type_sine_zone:
                    self.wave_settings_wave_type_sine_button.alpha = 0.8
                    if self.timer_wave_type_sine is None:
                        self.timer_wave_type_sine = time.time()
                    elif time.time() - self.timer_wave_type_sine >= self.hold_duration:
                        if self.player is not None:
                            self.player.wave_type = "sine"
                        self.sine, self.squere, self.saw, self.tringle, self.hand = True, False, False, False, False
                        self.timer_wave_type_sine = None
                else:
                    self.timer_wave_type_sine = None
            else:
                self.wave_settings_wave_type_sine_button.alpha = 1.0 
                self.timer_wave_type_sine = None

            # --- SQUARE ---
            if not self.squere:
                self.wave_settings_wave_type_squere_button.text_align = "mid"
                self.wave_settings_wave_type_squere_button.label = "     Squere     "
                self.slider_pw.visible = False
                self.wave_settings_wave_type_squere_button.alpha = 0.6
                if in_wave_button_type_squere_zone:
                    self.wave_settings_wave_type_squere_button.alpha = 0.8
                    if self.timer_wave_type_squere is None:
                        self.timer_wave_type_squere = time.time()
                    elif time.time() - self.timer_wave_type_squere >= self.hold_duration:
                        if self.player is not None:
                            self.player.wave_type = "square"
                        self.sine, self.squere, self.saw, self.tringle, self.hand = False, True, False, False, False
                        self.timer_wave_type_squere = None
                else:
                    self.timer_wave_type_squere = None
            else:
                self.wave_settings_wave_type_squere_button.alpha = 1.0
                self.timer_wave_type_squere = None

                self.wave_settings_wave_type_squere_button.alpha = 0.8
                self.wave_settings_wave_type_squere_button.text_align = "top"
                self.wave_settings_wave_type_squere_button.label = "  Pulse width  "
                self.slider_pw.visible = True

                if in_pw_slider_zone:
                    if self.timer_slider_pw is None:
                        self.timer_slider_pw = time.time()

                    elif time.time() - self.timer_slider_pw >= self.hold_duration:
                        if not self.slider_pw_locked:
                            relative_x = ix - self.slider_pw_x
                            self.slider_pw.value = max(
                                self.slider_pw.min_val,
                                min(
                                    self.slider_pw.max_val,
                                    (relative_x / self.slider_pw_w) * (self.slider_pw.max_val - self.slider_pw.min_val)
                                )
                            )

                        if self.player is not None:
                            self.player.pulse_width = self.slider_pw.value / 100


                        if self.slider_pw_hold_timer is None:
                            self.slider_pw_hold_timer = time.time()
                            self.slider_pw_snap_value = self.slider_pw.value

                        elif abs(ix - (self.slider_pw_x + (self.slider_pw_snap_value / self.slider_pw.max_val) * self.slider_pw_w)) <= 3:
                            if time.time() - self.slider_pw_hold_timer >= 2:
                                self.slider_pw.value = self.slider_pw_snap_value

                        else:
                            self.slider_pw_hold_timer = time.time()
                            self.slider_pw_snap_value = self.slider_pw.value


                        if self.slider_pw_last_ix is None:
                            self.slider_pw_last_ix = ix
                            self.slider_pw_stop_timer = time.time()

                        elif abs(ix - self.slider_pw_last_ix) <= 8:
                            if time.time() - self.slider_pw_stop_timer >= 1:
                                self.slider_pw.circle_color = (0, 200, 200)
                                self.slider_pw_locked = True

                        else:
                            self.slider_pw_last_ix = ix
                            self.slider_pw_stop_timer = time.time()
                            self.slider_pw_locked = False
                            self.slider_pw.circle_color = (50, 50, 50)

                else:

                    self.slider_pw_hold_timer = None
                    self.slider_pw_last_ix = None
                    self.slider_pw_stop_timer = None
                    self.slider_pw_locked = False
                    self.timer_slider_pw = None
                    self.slider_pw.circle_color = (50, 50, 50)

            # --- SAW ---
            if not self.saw:
                self.wave_settings_wave_type_saw_button.alpha = 0.6
                if in_wave_button_type_saw_zone:
                    self.wave_settings_wave_type_saw_button.alpha = 0.8
                    if self.timer_wave_type_saw is None:
                        self.timer_wave_type_saw = time.time()
                    elif time.time() - self.timer_wave_type_saw >= self.hold_duration:
                        if self.player is not None:
                            self.player.wave_type = "saw"
                        self.sine, self.squere, self.saw, self.tringle, self.hand = False, False, True, False, False
                        self.timer_wave_type_saw = None
                else:
                    self.timer_wave_type_saw = None
            else:
                self.wave_settings_wave_type_saw_button.alpha = 1.0
                self.timer_wave_type_saw = None

            # --- TRIANGLE ---
            if not self.tringle:
                self.wave_settings_wave_type_tringle_button.alpha = 0.6
                if in_wave_button_type_tringle_zone:
                    self.wave_settings_wave_type_tringle_button.alpha = 0.8
                    if self.timer_wave_type_tringle is None:
                        self.timer_wave_type_tringle = time.time()
                    elif time.time() - self.timer_wave_type_tringle >= self.hold_duration:
                        if self.player is not None:
                            self.player.wave_type = "triangle"
                        self.sine, self.squere, self.saw, self.tringle, self.hand = False, False, False, True, False
                        self.timer_wave_type_tringle = None
                else:
                    self.timer_wave_type_tringle = None
            else:
                self.wave_settings_wave_type_tringle_button.alpha = 1.0
                self.timer_wave_type_tringle = None
        else:
            self.slider_pw.visible = False

        # Hand Control
        if self.hand_control:
            in_play_button_zone = False
            in_midi_button_zone = False
            in_wave_button_zone = False
            in_wave_button_type_hand_control_zone = False
            in_wave_button_adsr_zone = False
            in_wave_button_type_zone = False

        if not self.hand_control:
            if self.wave_type_state == "on":
                if self.hand == True:
                    self.wave_settings_wave_type_hand_control_button.alpha = 1
                if self.hand == False:
                    self.wave_settings_wave_type_hand_control_button.alpha = 0.6
                    if in_wave_button_type_hand_control_zone:
                        self.wave_settings_wave_type_hand_control_button.alpha = 0.8
                        if self.timer_wave_type_hand_control is None:
                            self.timer_wave_type_hand_control = time.time()
                        elif time.time() - self.timer_wave_type_hand_control >= self.hold_duration:
                            self.hand_control = True
                            self.hand_wave = True
                            self.timer_wave_type_hand_control = None
                            self.hp = HandProcessor(draw_lines=True, draw_rect=True, draw_fing=False)

                            self.play_button.alpha = 0
                            self.midi_button.alpha = 0
                            self.wave_button.alpha = 0
                            self.wave_settings_adsr_button.alpha = 0
                            self.wave_settings_wave_type_button.alpha = 0
                            self.wave_settings_wave_type_hand_control_button.alpha = 0
                            self.wave_settings_wave_type_sine_button.alpha = 0
                            self.wave_settings_wave_type_squere_button.alpha = 0
                            self.wave_settings_wave_type_saw_button.alpha = 0
                            self.wave_settings_wave_type_tringle_button.alpha = 0
                            self.wave_settings_button.alpha = 0
                            
                            self.midi_state = "off"
                            self.wave_state = "off"
                            self.adsr_state = "off"
                            self.wave_type_state = "off"

                    else:
                        self.timer_wave_type_hand_control = None
            else:
                self.wave_settings_wave_type_hand_control_button.alpha = 0

        #Hand Control
        if self.hand_control:
            self.wave_settings_wave_type_hand_control_button.alpha = 0
            if self.play_state == "play" and self.player is not None:
                self.player.play()
                
            if in_hand_window_set_zone:
                self.wave_settings_wave_type_hand_control_window_button.alpha = 0.8
                if all_fingers is not None:
                    if self.last_fingers_pos is None:
                        self.last_fingers_pos = all_fingers
                        self.still_timer = time.time()
                    else:
                        moved = False
                        for i in range(5):
                            prev_x, prev_y = self.last_fingers_pos[i]
                            curr_x, curr_y = all_fingers[i]
                            
                            if abs(curr_x - prev_x) > 15 or abs(curr_y - prev_y) > 15:
                                moved = True
                                break
                        
                        if moved:
                            self.still_timer = time.time()
                            self.last_fingers_pos = all_fingers
                            self.fingers_are_still = False
                        else:
                            if time.time() - self.still_timer >= 2.0:
                                self.fingers_are_still = True
                                self.wave_settings_wave_type_hand_control_window_button.alpha = 0
                                self.hand_control = False
                                self.hand_wave = False
                                self.timer_wave_type_hand_control = None
                                self.hp = HandProcessor(draw_lines=False, draw_rect=False, draw_fing=True)
                                
                                self.midi_state = "off"
                                self.wave_state = "on"
                                self.adsr_state = "off"
                                self.wave_type_state = "on"
                                
                                self.play_button.alpha = 0.6
                                self.midi_button.alpha = 0.6
                                self.wave_button.alpha = 0.6
                                self.wave_settings_adsr_button.alpha = 0.6
                                self.wave_settings_wave_type_button.alpha = 0.6
                                self.wave_settings_wave_type_hand_control_button.alpha = 1
                                self.wave_settings_button.alpha = 0.1
                                self.wave_settings_wave_type_sine_button.alpha = 0.6
                                self.wave_settings_wave_type_squere_button.alpha = 0.6
                                self.wave_settings_wave_type_saw_button.alpha = 0.6
                                self.wave_settings_wave_type_tringle_button.alpha = 0.6
                                self.sine, self.squere, self.saw, self.tringle, self.hand = False, False, False, False, True
                                if self.play_state == "play" and self.player is not None:
                                    self.player.stop()
                else:
                    self.last_fingers_pos = None
                    self.still_timer = None
                    self.fingers_are_still = False
                    self.timer_hand_set = None
            else:
                self.wave_settings_wave_type_hand_control_window_button.alpha = 0.4

        # opracowanie Pitch
        if self.wave_state == "on":
            if in_pitch_button_zone and self.adsr_state == "off" and self.wave_type_state == "off":
                self.wave_settings_pitch_button.alpha = 0.8
            else:
                self.wave_settings_pitch_button.alpha = 0.6
                self.timer_pitch = None

            # --- HOLD / TOGGLE ---
            if in_pitch_button_zone and self.adsr_state == "off" and self.wave_type_state == "off":
                if self.timer_pitch is None:
                    self.timer_pitch = time.time()
                elif time.time() - self.timer_pitch >= self.hold_duration:
                    if self.pitch_state == "off":
                        self.pitch_state = "on"
                        self.wave_settings_pitch_window_button.alpha = 0.1
                    else:
                        self.pitch_state = "off"
                        self.wave_settings_pitch_window_button.alpha = 0
                    self.timer_pitch = None

        else:
            # --- RESET GDY WAVE OFF ---
            self.wave_settings_pitch_button.alpha = 0
            self.wave_settings_pitch_window_button.alpha = 0
            self.pitch_state = "off"
            self.timer_pitch = None

        # Semitones
        if self.pitch_state == "on":
            self.semitones_counter.alpha = 0.6

            # --- MINUS ---
            if in_semitones_counter_minus_zone:
                self.semitones_counter.alpha_minus = 0.8

                if self.semitones_counter_minus_timer is None:
                    self.semitones_counter_minus_timer = time.time()
                    self.semitones_counter_minus_last = None

                else:
                    if time.time() - self.semitones_counter_minus_timer >= self.hold_duration:
                        if self.semitones_counter_minus_last is None or (time.time() - self.semitones_counter_minus_last) >= self.repeat_interval:
                            if self.semitones_counter.value > self.semitones_counter.min_val:
                                self.semitones_counter.value -= 1
                                self.semitones_counter_minus_last = time.time()
            else:
                self.semitones_counter.alpha_minus = 0.6
                self.semitones_counter_minus_timer = None
                self.semitones_counter_minus_last = None

            # --- PLUS ---
            if in_semitones_counter_plus_zone:
                self.semitones_counter.alpha_plus = 0.8

                if self.semitones_counter_plus_timer is None:
                    self.semitones_counter_plus_timer = time.time()
                    self.semitones_counter_plus_last = None
                else:
                    if time.time() - self.semitones_counter_plus_timer >= self.hold_duration:
                        if self.semitones_counter_plus_last is None or (time.time() - self.semitones_counter_plus_last) >= self.repeat_interval:
                            if self.semitones_counter.value < self.semitones_counter.max_val:
                                self.semitones_counter.value += 1
                                self.semitones_counter_plus_last = time.time()
            else:
                self.semitones_counter.alpha_plus = 0.6
                self.semitones_counter_plus_timer = None
                self.semitones_counter_plus_last = None

        else:
            # pitch off
            self.semitones_counter.alpha = 0
            self.semitones_counter_minus_timer = None
            self.semitones_counter_minus_last = None
            self.semitones_counter_plus_timer = None
            self.semitones_counter_plus_last = None

        if self.semitones_counter.value > self.semitones_counter.max_val:
            self.semitones_counter.value = self.semitones_counter.max_val
        if self.semitones_counter.value < self.semitones_counter.min_val:
            self.semitones_counter.value = self.semitones_counter.min_val

        # Octave
        if self.pitch_state == "on":
            self.octave_counter.alpha = 0.6

            # --- MINUS ---
            if in_octave_counter_minus_zone:
                self.octave_counter.alpha_minus = 0.8

                if self.octave_minus_timer is None:
                    self.octave_minus_timer = time.time()
                    self.octave_minus_last = None

                else:
                    if time.time() - self.octave_minus_timer >= self.hold_duration:
                        if self.octave_minus_last is None or (time.time() - self.octave_minus_last) >= self.hold_duration:
                            if self.octave_counter.value > self.octave_counter.min_val:
                                self.octave_counter.value -= 1
                                self.octave_minus_last = time.time()
            else:
                self.octave_counter.alpha_minus = 0.6
                self.octave_minus_timer = None
                self.octave_minus_last = None

            # --- PLUS ---
            if in_octave_counter_plus_zone:
                self.octave_counter.alpha_plus = 0.8

                if self.octave_plus_timer is None:
                    self.octave_plus_timer = time.time()
                    self.octave_plus_last = None
                else:
                    if time.time() - self.octave_plus_timer >= self.hold_duration:
                        if self.octave_plus_last is None or (time.time() - self.octave_plus_last) >= self.hold_duration:
                            if self.octave_counter.value < self.octave_counter.max_val:
                                self.octave_counter.value += 1
                                self.octave_plus_last = time.time()
            else:
                self.octave_counter.alpha_plus = 0.6
                self.octave_plus_timer = None
                self.octave_plus_last = None

        else:
            # pitch off
            self.octave_counter.alpha = 0
            self.octave_minus_timer = None
            self.octave_minus_last = None
            self.octave_plus_timer = None
            self.octave_plus_last = None

        if self.octave_counter.value > self.octave_counter.max_val:
            self.octave_counter.value = self.octave_counter.max_val
        if self.octave_counter.value < self.octave_counter.min_val:
            self.octave_counter.value = self.octave_counter.min_val


        # Cents
        if self.pitch_state == "on" and in_cents_reset_zone:
            if self.timer_cents_reset is None:
                self.timer_cents_reset = time.time()
            elif time.time() - self.timer_cents_reset >= self.hold_duration:
                self.slider_cents.reset_value(0)
                self.timer_cents_reset = None
        else:
            self.timer_cents_reset = None

        # Mono Toggle
        if self.pitch_state == "on" and not self.poly_glide_toggle.state:
            self.mono_toggle.alpha = 0.8
            if in_mono_toggle_zone:
                if self.timer_mono_toggle is None:
                    self.timer_mono_toggle = time.time()
                elif time.time() - self.timer_mono_toggle >= self.hold_duration:
                    if not self.mono_toggle.state:
                        self.mono_toggle.state = True
                    else:
                        self.mono_toggle.state = False
                        self.legato_toggle.state = False
                    self.timer_mono_toggle = None
            else:
                self.timer_mono_toggle = None
        elif self.pitch_state == "on" and self.poly_glide_toggle.state:
            self.mono_toggle.alpha = 0.5
            self.timer_mono_toggle = None

        # Legato Toggle
        if self.pitch_state == "on" and not self.poly_glide_toggle.state:
            self.legato_toggle.alpha = 0.8
            if in_legato_toggle_zone:
                if self.timer_legato_toggle is None:
                    self.timer_legato_toggle = time.time()
                elif time.time() - self.timer_legato_toggle >= self.hold_duration:
                    if not self.legato_toggle.state:
                        self.legato_toggle.state = True
                        self.mono_toggle.state = True
                    else:
                        self.legato_toggle.state = False
                    self.timer_legato_toggle = None
            else:
                self.timer_legato_toggle = None
        elif self.pitch_state == "on" and self.poly_glide_toggle.state:
            self.legato_toggle.alpha = 0.5
            self.timer_legato_toggle = None

        # Poly Glide Toggle
        if (self.pitch_state == "on" and not self.mono_toggle.state 
            and not self.legato_toggle.state):
            self.poly_glide_toggle.alpha = 0.8
            if in_poly_glide_toggle_zone:
                if self.timer_poly_glide_toggle is None:
                    self.timer_poly_glide_toggle = time.time()
                elif time.time() - self.timer_poly_glide_toggle >= self.hold_duration:
                    if not self.poly_glide_toggle.state:
                        self.poly_glide_toggle.state = True
                    else:
                        self.poly_glide_toggle.state = False
                    self.timer_poly_glide_toggle = None
            else:
                self.timer_poly_glide_toggle = None
        elif self.pitch_state == "on" and (self.mono_toggle.state or self.legato_toggle.state):
            self.poly_glide_toggle.alpha = 0.5
            self.timer_poly_glide_toggle = None

        # Glide Mode Legato
        if self.pitch_state == "on" and in_glide_mode_legato_zone:
            if self.timer_glide_mode_legato is None:
                self.timer_glide_mode_legato = time.time()
                self.wave_settings_pitch_glide_mode_legato_button.alpha = 0.8
            elif time.time() - self.timer_glide_mode_legato >= self.hold_duration:
                if self.glide_mode_legato_state == "off":
                    self.glide_mode_legato_state = "on"
                    self.glide_mode_always_state = "off"
                    self.timer_glide_mode_legato = None
                else:
                    self.glide_mode_legato_state = "off"
                    self.glide_mode_always_state = "on"
                    self.timer_glide_mode_legato = None
        else:
            self.timer_glide_mode_legato = None

        # Glide Mode Always
        if self.pitch_state == "on" and in_glide_mode_always_zone:
            if self.timer_glide_mode_always is None:
                self.timer_glide_mode_always = time.time()
                self.wave_settings_pitch_glide_mode_always_button.alpha = 0.8
            elif time.time() - self.timer_glide_mode_always >= self.hold_duration:
                if self.glide_mode_always_state == "off":
                    self.glide_mode_always_state = "on"
                    self.glide_mode_legato_state = "off"
                    self.timer_glide_mode_always = None
                else:
                    self.glide_mode_always_state = "off"
                    self.glide_mode_legato_state = "on"
                    self.timer_glide_mode_always = None
        else:
            self.timer_glide_mode_always = None

        # Glide Time Slider
        if in_glide_time_slider_zone and self.pitch_state == "on":
            if self.timer_glide_time_zone is None:
                self.timer_glide_time_zone = time.time()
                self.slider_active = False
            elif time.time() - self.timer_glide_time_zone >= self.hold_duration:
                self.slider_active = True

            if self.slider_active:
                if not getattr(self, "slider_glide_time_locked", False):
                    gt_w = getattr(self, "slider_gt_w", 0) or 0
                    if gt_w != 0:
                        rel = max(0.0, min(1.0, (ix - getattr(self, "slider_gt_x", 0)) / float(gt_w)))
                        self.slider_glide_time.value = (self.slider_glide_time.min_val +
                                                        rel * (self.slider_glide_time.max_val - self.slider_glide_time.min_val))

                if getattr(self, "slider_glide_time_hold_timer", None) is None:
                    self.slider_glide_time_hold_timer = time.time()
                    self.slider_glide_time_snap_value = self.slider_glide_time.value
                else:
                    minv = self.slider_glide_time.min_val
                    maxv = self.slider_glide_time.max_val
                    rangev = (maxv - minv) if (maxv - minv) != 0 else None
                    if rangev is not None:
                        snap_x = (self.slider_gt_x +
                                ((self.slider_glide_time_snap_value - minv) / rangev) * self.slider_gt_w)
                    else:
                        snap_x = None

                    if snap_x is not None and abs(ix - snap_x) <= 3 and time.time() - self.slider_glide_time_hold_timer >= 2:
                        self.slider_glide_time.value = self.slider_glide_time_snap_value
                    else:
                        self.slider_glide_time_hold_timer = time.time()
                        self.slider_glide_time_snap_value = self.slider_glide_time.value

                if getattr(self, "slider_glide_time_last_ix", None) is None:
                    self.slider_glide_time_last_ix = ix
                    self.slider_glide_time_stop_timer = time.time()
                elif abs(ix - self.slider_glide_time_last_ix) <= 8:
                    if time.time() - self.slider_glide_time_stop_timer >= 1:
                        try:
                            self.slider_glide_time.circle_color = (0, 200, 200)
                        except Exception:
                            pass
                        self.slider_glide_time_locked = True
                else:
                    self.slider_glide_time_last_ix = ix
                    self.slider_glide_time_stop_timer = time.time()
                    self.slider_glide_time_locked = False
                    try:
                        self.slider_glide_time.circle_color = (50, 50, 50)
                    except Exception:
                        pass

        else:
            self.slider_glide_time_hold_timer = None
            self.slider_glide_time_last_ix = None
            self.slider_glide_time_stop_timer = None
            self.slider_glide_time_locked = False
            self.slider_active = False
            try:
                self.slider_glide_time.circle_color = (50, 50, 50)
            except Exception:
                pass
            self.slider_glide_time_snap_value = None
            self.timer_glide_time_zone = None


        # Phase Slider
        if in_phase_slider_zone and self.pitch_state == "on":
            if self.phase_random_state == "off":
                if self.timer_slider_phase_zone is None:
                    self.timer_slider_phase_zone = time.time()
                elif time.time() - self.timer_slider_phase_zone >= self.hold_duration:
                    if not self.slider_phase_locked:
                        relative_x = ix - self.slider_phase_x
                        rel = relative_x / float(self.slider_phase_w) if self.slider_phase_w != 0 else 0.0
                        rel = max(0.0, min(1.0, rel))
                        v = (self.slider_phase.min_val + 
                             rel * (self.slider_phase.max_val - self.slider_phase.min_val))
                        self.slider_phase.value = v

                    if self.slider_phase_hold_timer is None:
                        self.slider_phase_hold_timer = time.time()
                        self.slider_phase_snap_value = self.slider_phase.value
                    else:
                        if self.slider_phase.max_val != self.slider_phase.min_val:
                            snap_x = (self.slider_phase_x + 
                                     ((self.slider_phase_snap_value - self.slider_phase.min_val) /
                                      (self.slider_phase.max_val - self.slider_phase.min_val)) * 
                                     self.slider_phase_w)
                        else:
                            snap_x = self.slider_phase_x
                        if abs(ix - snap_x) <= 3:
                            if time.time() - self.slider_phase_hold_timer >= 2:
                                self.slider_phase.value = self.slider_phase_snap_value
                        else:
                            self.slider_phase_hold_timer = time.time()
                            self.slider_phase_snap_value = self.slider_phase.value

                    if self.slider_phase_last_ix is None:
                        self.slider_phase_last_ix = ix
                        self.slider_phase_stop_timer = time.time()
                    elif abs(ix - self.slider_phase_last_ix) <= 8:
                        if time.time() - self.slider_phase_stop_timer >= 1:
                            self.slider_phase.circle_color = (0, 200, 200)
                            self.slider_phase_locked = True
                    else:
                        self.slider_phase_last_ix = ix
                        self.slider_phase_stop_timer = time.time()
                        if self.slider_phase_locked:
                            self.slider_phase_locked = False
                        self.slider_phase.circle_color = (50, 50, 50)

            else:
                self.timer_slider_phase_zone = None
                self.slider_phase_hold_timer = None
                self.slider_phase_last_ix = None
                self.slider_phase_stop_timer = None
                self.slider_phase_locked = False
                self.slider_phase.circle_color = (50, 50, 50)
        else:
            self.timer_slider_phase_zone = None
            self.slider_phase_hold_timer = None
            self.slider_phase_last_ix = None
            self.slider_phase_stop_timer = None
            self.slider_phase_locked = False
            self.slider_phase.circle_color = (50, 50, 50)

        # Random Phase
        if self.pitch_state == "on" and in_phase_random_zone:
            if self.timer_phase_random is None:
                self.timer_phase_random = time.time()
            elif time.time() - self.timer_phase_random >= self.hold_duration:
                if self.phase_random_state == "off":
                    self.phase_random_state = "on"
                else:
                    self.phase_random_state = "off"
                self.timer_phase_random = None
        else:
            self.timer_phase_random = None


    def process_midi_window(self, ix, iy, all_fingers):
        # MIDI przycisk
        if (not self.hand_control and self.wave_state == "off" and 
            self.midi_x <= ix <= self.midi_x + self.midi_size_w and 
            self.midi_y <= iy <= self.midi_y + self.midi_size_h):
            
            if self.timer_midi is None:
                self.midi_button.alpha = 0.8
                self.timer_midi = time.time()
            elif time.time() - self.timer_midi >= self.hold_duration:
                if self.midi_state == "off":
                    self.midi_state = "on"
                    self.midi_window_button.alpha = 0.6
                    self.midi_window_ok_button.alpha = 0.6
                    self.midi_window_cancel_button.alpha = 0.6

                    for row in self.rows:
                        for b in row:
                            b.alpha = 0.0
                    for b in self.rows[self.midi_button_row]:
                        b.alpha = 0.3

                    # strzala na dol
                    if self.midi_button_row == len(self.rows) - 1:
                        self.midi_window_down_button.alpha = 0
                    else:
                        self.midi_window_down_button.alpha = 0.6

                else:
                    self.midi_state = "off"
                    self.midi_window_button.alpha = 0.0
                    self.midi_window_ok_button.alpha = 0.0
                    self.midi_window_cancel_button.alpha = 0.0
                    self.midi_window_down_button.alpha = 0.0
                    for row in self.rows:
                        for b in row:
                            b.alpha = 0.0

                self.timer_midi = None
        else:
            self.timer_midi = None
            if not self.hand_control:
                self.midi_button.alpha = 0.6

        if self.midi_state == "on":
            in_midi_button_down_zone = (self.midi_down_x <= ix <= self.midi_down_x + self.midi_size_down_w and 
                                       self.midi_down_y <= iy <= self.midi_down_y + self.midi_size_down_h)
            
            if in_midi_button_down_zone:
                if self.timer_down is None:
                    self.timer_down = time.time()
                elif time.time() - self.timer_down >= self.hold_duration:
                    if self.midi_button_row < len(self.rows) - 1:
                        self.midi_button_row += 1
                        for row in self.rows:
                            for b in row:
                                b.alpha = 0.0
                        for b in self.rows[self.midi_button_row]:
                            b.alpha = 0.3

                        if self.midi_button_row == len(self.rows) - 1:
                            self.midi_window_down_button.alpha = 0
                        else:
                            self.midi_window_down_button.alpha = 0.6

                    self.timer_down = None
            else:
                self.timer_down = None

            # swipe w gore
            in_midi_button_up_zone = (self.midi_up_x <= ix <= self.midi_up_x + self.midi_size_up_w and 
                                     self.midi_up_y <= iy <= self.midi_up_y + self.midi_size_up_h)
            
            if in_midi_button_up_zone:
                if self.timer_up is None:
                    self.timer_up = time.time()
                elif time.time() - self.timer_up >= self.hold_duration:
                    if self.midi_button_row > 0:
                        self.midi_button_row -= 1
                    for row in self.rows:
                        for b in row:
                            b.alpha = 0.0
                    for b in self.rows[self.midi_button_row]:
                        b.alpha = 0.3
                    self.timer_up = None
            else:
                self.timer_up = None

            self.midi_window_up_button.alpha = 0.6 if self.midi_button_row > 0 else 0
            self.midi_window_down_button.alpha = 0.6 if self.midi_button_row < len(self.rows) - 1 else 0

            for b in self.rows[self.midi_button_row]:
                if not hasattr(b, "hover_start"):
                    b.hover_start = None

                btn_x, btn_y = b.pos
                btn_w, btn_h = b.size

                in_zone = btn_x <= ix <= btn_x + btn_w and btn_y <= iy <= btn_y + btn_h

                if in_zone:
                    if b.hover_start is None:
                        b.hover_start = time.time()
                    elif time.time() - b.hover_start >= 2:
                        self.active_button = b
                else:
                    b.hover_start = None

                if self.active_button == b:
                    b.alpha = 0.8
                elif in_zone:
                    b.alpha = 0.4
                else:
                    b.alpha = 0.1

            in_midi_button_ok_zone = (self.midi_ok_x <= ix <= self.midi_ok_x + self.midi_ok_w and 
                                     self.midi_ok_y <= iy <= self.midi_ok_y + self.midi_ok_h)
            
            if in_midi_button_ok_zone:
                self.midi_window_ok_button.alpha = 0.8

                if self.timer_midi_ok is None:
                    self.timer_midi_ok = time.time()

                elif time.time() - self.timer_midi_ok >= self.hold_duration:
                    if self.active_button is not None:
                        midi_file_path = os.path.join(self.midi_folder, self.active_button.label)
                        threading.Thread(target=self.load_midi, args=(midi_file_path,), daemon=True).start()

                    self.midi_state = "off"
                    self.play_state = "play"
                    self.play_button.label = "play"
                    self.midi_button_row = 0
                    self.midi_window_button.alpha = 0.0
                    self.midi_window_ok_button.alpha = 0.0
                    self.midi_window_cancel_button.alpha = 0.0
                    self.midi_window_down_button.alpha = 0.0
                    self.midi_window_up_button.alpha = 0.0

                    for row in self.rows:
                        for b in row:
                            b.alpha = 0.0

                    self.timer_midi_ok = None
            elif not in_midi_button_ok_zone and self.midi_state == "on":
                self.midi_window_ok_button.alpha = 0.3
                self.timer_midi_ok = None

            in_midi_button_cancel_zone = (self.midi_cancel_x <= ix <= self.midi_cancel_x + self.midi_cancel_w and 
                                         self.midi_cancel_y <= iy <= self.midi_cancel_y + self.midi_cancel_h)
            
            if in_midi_button_cancel_zone:
                self.midi_window_cancel_button.alpha = 0.8
                if self.timer_cancel is None:
                    self.timer_cancel = time.time()
                elif time.time() - self.timer_cancel >= self.hold_duration:
                    self.midi_state = "off"
                    self.midi_button_row = 0
                    self.midi_window_button.alpha = 0.0
                    self.midi_window_ok_button.alpha = 0.0
                    self.midi_window_cancel_button.alpha = 0.0
                    self.midi_window_down_button.alpha = 0.0
                    self.midi_window_up_button.alpha = 0.0
                    for row in self.rows:
                        for b in row:
                            b.alpha = 0.0
                    self.timer_cancel = None
            elif not in_midi_button_cancel_zone and self.midi_state == "on":
                self.midi_window_cancel_button.alpha = 0.3
                self.timer_cancel = None
            else:
                self.timer_cancel = None
                self.midi_window_cancel_button.alpha = 0

    def draw(self, img):
        """
        Rysowanie wszystkich elemetow na ekranie
        """
        img = self.play_button.draw(img)
        img = self.midi_button.draw(img)
        img = self.wave_button.draw(img)
        img = self.midi_window_button.draw(img)
        img = self.midi_window_ok_button.draw(img)
        img = self.midi_window_cancel_button.draw(img)
        img = self.midi_window_down_button.draw(img)
        img = self.midi_window_up_button.draw(img)
        img = self.wave_settings_button.draw(img)
        img = self.wave_settings_adsr_button.draw(img)
        img = self.wave_settings_adsr_window_button.draw(img)
        img = self.wave_settings_adsr_attack_button.draw(img)
        img = self.slider.draw(img)
        img = self.wave_settings_adsr_release_button.draw(img)
        img = self.slider_release.draw(img)
        img = self.wave_settings_adsr_decay_button.draw(img)
        img = self.slider_decay.draw(img)
        img = self.wave_settings_adsr_sustain_button.draw(img)
        img = self.slider_sustain.draw(img)
        img = self.wave_settings_adsr_reset_button.draw(img)
        img = self.wave_settings_pitch_window_semitones_button.draw(img)
        img = self.wave_settings_pitch_window_octave_button.draw(img)
        img = self.wave_settings_pitch_window_button.draw(img)
        img = self.wave_settings_wave_type_button.draw(img)
        img = self.wave_settings_wave_type_window_button.draw(img)
        img = self.wave_settings_wave_type_sine_button.draw(img)
        img = self.wave_settings_wave_type_squere_button.draw(img)
        img = self.wave_settings_wave_type_saw_button.draw(img)
        img = self.wave_settings_wave_type_tringle_button.draw(img)
        img = self.wave_settings_wave_type_hand_control_button.draw(img)
        img = self.wave_settings_wave_type_hand_control_window_button.draw(img)
        img = self.slider_pw.draw(img)
        img = self.wave_settings_pitch_button.draw(img)
        img = self.semitones_counter.draw(img)
        img = self.octave_counter.draw(img)
        img = self.wave_settings_pitch_cents_button.draw(img)
        img = self.slider_cents.draw(img)
        img = self.wave_settings_pitch_mono_button.draw(img)
        img = self.mono_toggle.draw(img)
        img = self.wave_settings_pitch_legato_button.draw(img)
        img = self.legato_toggle.draw(img)
        img = self.wave_settings_pitch_poly_glide_button.draw(img)
        img = self.poly_glide_toggle.draw(img)
        img = self.wave_settings_pitch_glide_mode_legato_button.draw(img)
        img = self.wave_settings_pitch_glide_mode_button.draw(img)
        img = self.wave_settings_pitch_glide_mode_always_button.draw(img)
        img = self.wave_settings_pitch_glide_time_button.draw(img)
        img = self.slider_glide_time.draw(img)
        img = self.wave_settings_pitch_cents_reset_button.draw(img)
        img = self.wave_settings_pitch_phase_button.draw(img)
        img = self.slider_phase.draw(img)
        img = self.wave_settings_pitch_phase_random_button.draw(img)

        if self.midi_state == "on":
            for btn in self.rows[self.midi_button_row]:
                img = btn.draw(img)
                
        return img
    
    def update_adsr_params(self):
        if self.player is not None:
            self.player.attack = self.slider.value
            self.player.decay = self.slider_decay.value
            self.player.sustain = self.slider_sustain.value
            self.player.release = self.slider_release.value

    def update_hand_wave(self, wave_points):
        if self.hand_wave and self.player is not None:
            if isinstance(self.player, MidiPlayer) and self.player.wave_type != "hand":
                self.player.wave_type = "hand"

            table_size = self.player.tbl.getSize()
            points = [(0, 0.0)] + [
                (int(x * (table_size - 1)), y) 
                for (x, y) in wave_points
            ] + [(table_size - 1, 0.0)]
            
            self.current_hand_points = points 
            
            self.player.update_table(points)
