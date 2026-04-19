import cv2
import numpy as np

class Cv2Button:
    def __init__(
        self,
        label="PLAY",
        pos=(50, 50),
        size=(120, 50),
        color=(255, 255, 255),
        alpha=0.6,
        text_color=(0, 0, 0),
        draw_arrow=False,
        arrow_dir="down",
        text_align="center",
        thickness=2
    ):
        self.label = label
        self.pos = pos
        self.size = size
        self.color = color
        self.alpha = alpha
        
        self._current_alpha = alpha  
        self._text_alpha = 1.0 if alpha > 0 else 0.0 
        
        self.text_color = text_color
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.thickness = thickness
        self.draw_arrow_flag = draw_arrow
        self.arrow_dir = arrow_dir
        self.text_align = text_align

    def draw(self, frame):
        fade_speed = 0.2  #szybkosc animacji
        
        if self._current_alpha < self.alpha:
            self._current_alpha = min(self._current_alpha + fade_speed, self.alpha)
        elif self._current_alpha > self.alpha:
            self._current_alpha = max(self._current_alpha - fade_speed, self.alpha)

        target_text_alpha = 1.0 if self.alpha > 0 else 0.0
        if self._text_alpha < target_text_alpha:
            self._text_alpha = min(self._text_alpha + fade_speed * 2, target_text_alpha)
        elif self._text_alpha > target_text_alpha:
            self._text_alpha = max(self._text_alpha - fade_speed * 2, target_text_alpha)

        if self._current_alpha <= 0 and self._text_alpha <= 0:
            return frame

        x, y = self.pos
        w, h = self.size

        # tlo
        if self._current_alpha > 0:
            bg_overlay = frame.copy()
            cv2.rectangle(bg_overlay, (x, y), (x + w, y + h), self.color, -1)
            cv2.addWeighted(bg_overlay, self._current_alpha, frame, 1 - self._current_alpha, 0, frame)

        if self._text_alpha > 0:
            text_overlay = frame.copy()
            
            if self.draw_arrow_flag:
                # strzalka
                if self.arrow_dir == "down":
                    start_point = (x + w//2, y + h//4)
                    end_point   = (x + w//2, y + 3*h//4)
                elif self.arrow_dir == "up":
                    start_point = (x + w//2, y + 3*h//4)
                    end_point   = (x + w//2, y + h//4)

                cv2.arrowedLine(text_overlay, start_point, end_point, self.text_color, 2, tipLength=0.4)
            else:
                # tekst z masztabowaniem
                font_scale = 2.0
                max_width = 0.9 * w
                max_height = 0.8 * h
                while True:
                    text_size = cv2.getTextSize(self.label, self.font, font_scale, self.thickness)[0]
                    if text_size[0] > max_width or text_size[1] > max_height:
                        font_scale -= 0.05
                    else:
                        break

                text_size = cv2.getTextSize(self.label, self.font, font_scale, self.thickness)[0]
                text_w, text_h = text_size

                # x zawsze centrum
                text_x = x + (w - text_w) // 2

                # y w zaleznosci od trybu
                if self.text_align == "top":
                    text_y = y + text_h + h // 10
                elif self.text_align == "bottom":
                    text_y = y + h - h // 10
                else: 
                    text_y = y + (h + text_h) // 2
                
                cv2.putText(text_overlay, self.label, (text_x, text_y),
                            self.font, font_scale, self.text_color, self.thickness)

            cv2.addWeighted(text_overlay, self._text_alpha, frame, 1 - self._text_alpha, 0, frame)

        return frame