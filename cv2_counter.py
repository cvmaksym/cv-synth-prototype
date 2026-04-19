import cv2
import numpy as np
from cv2_button import Cv2Button

class Cv2Counter:
    def __init__(
        self,
        pos=(50, 50),
        size=(200, 60),
        value=0,
        step=1,
        min_val=-24,
        max_val=24,
        border_color=(180,180,180),
        text_color=(0,0,0),
        alpha=0.6,
        alpha_minus=None,
        alpha_plus=None,
        font_scale=0.45,
        font_thickness=2,
        font=cv2.FONT_HERSHEY_SIMPLEX
    ):
        self.x, self.y = pos
        self.w, self.h = size

        self.value = value
        self.step = step
        self.min_val = min_val
        self.max_val = max_val

        btn_w = self.w // 4
        btn_h = self.h

        if alpha_minus is None:
            alpha_minus = alpha
        if alpha_plus is None:
            alpha_plus = alpha

        self.alpha = alpha
        self.alpha_minus = alpha_minus
        self.alpha_plus = alpha_plus

        self.minus_btn = Cv2Button(
            label="-",
            pos=(self.x, self.y),
            size=(btn_w, btn_h),
            alpha=alpha_minus
        )

        self.plus_btn = Cv2Button(
            label="+",
            pos=(self.x + self.w - btn_w, self.y),
            size=(btn_w, btn_h),
            alpha=alpha_plus
        )

        self.border_color = border_color
        self.text_color = text_color

        self.font_scale = font_scale
        self.font_thickness = font_thickness
        self.font = font
        self._btn_w = btn_w

    def draw(self, frame):
        if frame is None:
            return None

        # jesli alpha=0 jest niewidoczny
        if self.alpha == 0:
            return frame

        self.minus_btn.alpha = self.alpha_minus
        self.plus_btn.alpha = self.alpha_plus

        # kontur
        if self.border_color is not None and (self.alpha_minus > 0 or self.alpha_plus > 0):
            cv2.rectangle(
                frame,
                (self.x, self.y),
                (self.x + self.w, self.y + self.h),
                self.border_color,
                3
            )

        self.minus_btn.draw(frame)
        self.plus_btn.draw(frame)

        # tekst
        if self.text_color is not None and (self.alpha_minus > 0 or self.alpha_plus > 0):
            value_text = str(self.value)
            (tw, th), _ = cv2.getTextSize(
                value_text,
                self.font,
                self.font_scale,
                self.font_thickness
            )
            central_x = self.x + self._btn_w
            central_w = self.w - 2 * self._btn_w
            cx = central_x + (central_w - tw) // 2
            cy = self.y + (self.h - th) // 2 + th
            cv2.putText(
                frame,
                value_text,
                (int(cx), int(cy)),
                self.font,
                self.font_scale,
                self.text_color,
                self.font_thickness,
                cv2.LINE_AA
            )

        return frame

    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def size(self):
        return (self.w, self.h)
