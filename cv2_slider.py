import cv2
import numpy as np

class Cv2Slider:
    def __init__(self, pos=(50,50), size=(200,30), min_val=0, max_val=127, value=0,
                 font_scale=0.5, font_thickness=1, font_color=(0,0,0), unit="sec",
                 nonlinear_factor=0.5, precision_switch=1.0, step=None, visible=True, circle_color=(50, 50, 50)):

        self.pos = pos
        self.size = size
        self.min_val = float(min_val)
        self.max_val = float(max_val)

        self.font_scale = font_scale
        self.font_thickness = font_thickness
        self.font_color = font_color
        self.unit = unit
        self.visible = visible
        self.circle_pos = None
        self.circle_color = circle_color

        # nielinejnosc
        self.nonlinear_factor = float(nonlinear_factor)
        self.precision_switch = precision_switch
        self.step = None if step is None else float(step)

        self._initial_value = float(value)
        self._value = self._inverse_nonlinear(value)
        self._moved = False

        # grafika
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.radius = size[1] // 6
        self.line_color = (150,150,150)
        self.circle_color = (80,80,80)

    def _inverse_nonlinear(self, display_value):
        denom = (self.max_val - self.min_val) or 1e-6
        rel = (display_value - self.min_val) / denom
        rel = np.clip(rel, 0.0, 1.0)
        eps = 0.01
        if self.nonlinear_factor == 0:
            inv = rel
        else:
            power = (1 - self.nonlinear_factor + eps)
            inv = rel ** power
        return self.min_val + inv * denom

    def _apply_step(self, v):
        if self.step is None or self.step <= 0:
            return v
        return round(v / self.step) * self.step

    @property
    def value(self):
        if not self._moved:
            t = self._initial_value
        else:
            t = self.get_time_value()
        return self._apply_step(t)

    def reset_value(self, display_value):
        self._initial_value = float(display_value)   
        self._value = self._inverse_nonlinear(display_value) 
        self._moved = False
        
    @value.setter
    def value(self, v):
        v = float(v)
        denom = (self.max_val - self.min_val) or 1e-6
        self._value = np.clip(v, self.min_val, self.max_val)
        self._moved = True

    def get_time_value(self):
        denom = (self.max_val - self.min_val) or 1e-6
        rel = (self._value - self.min_val) / denom
        rel = np.clip(rel, 0.0, 1.0)
        eps = 0.01
        if self.nonlinear_factor == 0:
            t_rel = rel
        else:
            power = 1.0 / (1.0 - self.nonlinear_factor + eps)
            t_rel = rel ** power
        return self.min_val + t_rel * denom

    def get_display_text(self):
        t = self.value
        if self.step is not None and self.step >= 1 and abs(round(self.step) - self.step) < 1e-9:
            return f"{int(round(t))} {self.unit}"

        if t <= self.precision_switch:
            return f"{t:.2f} {self.unit}"
        else:
            return f"{t:.1f} {self.unit}"

    def draw(self, frame):
        x, y = self.pos
        w, h = self.size

        # pozycja krega
        denom = (self.max_val - self.min_val) or 1e-6
        rel = (self._value - self.min_val) / denom
        rel = np.clip(rel, 0.0, 1.0)

        cx = int(x + rel * w)
        cy = int(y + h // 2)
        self.circle_pos = (cx, cy)
        
        if not self.visible:
            return frame

        cv2.line(frame, (x, cy), (x + w, cy),
                 self.line_color, max(2, h // 6), cv2.LINE_AA)

        cv2.circle(frame, (cx, cy), self.radius,
                   self.circle_color, -1, cv2.LINE_AA)

        text = self.get_display_text()
        (tw, th), _ = cv2.getTextSize(text, self.font,
                                      self.font_scale, self.font_thickness)
        cv2.putText(frame, text,
                    (cx - tw // 2, cy - self.radius - 2),
                    self.font, self.font_scale,
                    self.font_color, self.font_thickness, cv2.LINE_AA)

        return frame
