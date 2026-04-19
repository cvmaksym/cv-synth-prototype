import cv2
import numpy as np

class Cv2Toggle:
    """
    - Stan ON świeci, stan OFF jest matowy/szary.
    - Bardzo czytelny geometrycznie.
    """
    def __init__(
        self,
        pos=(50, 50),
        size=(120, 40),
        label="SYSTEM",
        state=False,
        on_color=(0, 255, 100),   # Jaskrawy kolor ON
        off_color=(60, 60, 60),   # Ciemny kolor tła suwaka OFF
        plate_color=(30, 30, 30), # Tło całego komponentu
        knob_color=(200, 200, 200), # (Ignorowane w tym stylu na rzecz kontrastu)
        alpha=1.0,
        radius=2,
        font=cv2.FONT_HERSHEY_SIMPLEX,
        text_color=(255, 255, 255),
        label_color=(180, 180, 180),
        toggle_on_click=True
    ):
        self.x, self.y = pos
        self.w, self.h = size
        self.label = label
        self.state = bool(state)
        self.on_color = on_color
        self.off_color = off_color
        self.plate_color = plate_color
        self.knob_color = knob_color
        self.alpha = alpha
        self.radius = radius 
        self.font = font
        self.text_color = text_color
        self.label_color = label_color
        self.toggle_on_click = toggle_on_click

    def inside(self, px, py):
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h

    def set_state(self, value: bool):
        self.state = bool(value)

    def toggle(self):
        self.state = not self.state

    @property
    def pos(self):
        return (self.x, self.y)
    
    @property
    def size(self):
        return (self.w, self.h)

    def draw(self, frame):
        overlay = frame.copy()
        
        # 1. TŁO
        cv2.rectangle(overlay, (self.x, self.y), (self.x + self.w, self.y + self.h), self.plate_color, -1)
        cv2.rectangle(overlay, (self.x, self.y), (self.x + self.w, self.y + self.h), (50, 50, 50), 1)

        # odstepy
        pad = 4
        slider_w = (self.w // 2) - pad
        slider_h = self.h - (2 * pad)

        # 2. LOGIKA POZYCJI I KOLORU 
        if self.state:
            slider_x = self.x + (self.w // 2) + (pad // 2)
            slider_fill = self.on_color 
            track_color = tuple(int(c * 0.3) for c in self.on_color)
            
            cv2.rectangle(overlay, (self.x + pad, self.y + pad + slider_h//2 - 2), 
                          (slider_x, self.y + pad + slider_h//2 + 2), track_color, -1)
        else:
            slider_x = self.x + pad
            slider_fill = (90, 90, 90) 

        # 3. RYSOWANIE SUWAKA
        cv2.rectangle(overlay, (slider_x, self.y + pad), (slider_x + slider_w, self.y + pad + slider_h), slider_fill, -1)
        
        # 4. DODATKOWY DETAL NA SUWAKU (dla tekstury)
        # Trzy małe kreseczki na środku suwaka (chwytak/grip)
        grip_color = (40, 40, 40) if self.state else (120, 120, 120)
        center_x = slider_x + slider_w // 2
        center_y = self.y + self.h // 2
        for i in range(-3, 4, 3):
            cv2.line(overlay, (center_x + i, center_y - 5), (center_x + i, center_y + 5), grip_color, 1)

        # 5. MIESZANIE Z PRZEZROCZYSTOŚCIĄ
        if self.alpha < 1.0:
            cv2.addWeighted(overlay, self.alpha, frame, 1 - self.alpha, 0, frame)
        else:
            frame[self.y:self.y+self.h, self.x:self.x+self.w] = \
                overlay[self.y:self.y+self.h, self.x:self.x+self.w]

        # 6. ETYKIETA (LABEL) - Bez kropki
        label_fs = max(0.4, self.h / 120.0 * 1.5)
        lbl_col = self.text_color if self.state else self.label_color
        
        cv2.putText(frame, self.label, (self.x, self.y - 6), self.font, label_fs, lbl_col, 1, cv2.LINE_AA)

        return frame