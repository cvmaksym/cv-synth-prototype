import cv2
from gui import MidiControllerGUI

def main():
    # Tworzenie instancji GUI
    gui = MidiControllerGUI()
    # Pętla główna
    while True:
        # Aktualizacja parametrów odtwarzacza na podstawie stanu UI
        gui.update_player_params()
        # Odczyt klatki z kamery
        success, img = gui.cap.read()
        if not success:
            break
        # Odbicie lustrzane (Mirror)
        img = cv2.flip(img, 1)    
        # Przetwarzanie dłoni
        result = gui.hp.process(img)        
        # Obsługa gestów i interakcji z UI
        if result is not None:
            gui.process_hand_gesture(result, img)        
        # Rysowanie wszystkich komponentów UI
        img = gui.draw(img)
        # Wyświetlanie wyniku
        cv2.imshow("MIDI Controller", img)        
        # Wyjście po naciśnięciu 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Czyszczenie zasobów
    if gui.player is not None:
        gui.player.stop()
    gui.cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()