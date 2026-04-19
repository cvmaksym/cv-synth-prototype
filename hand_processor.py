import cv2
import mediapipe as mp
from orientation import OrientationSmoother

class HandProcessor:
    def __init__(self, draw_lines=True, draw_rect=True, draw_fing=True):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.orient = OrientationSmoother()
        self.draw_lines = draw_lines
        self.draw_rect = draw_rect
        self.draw_fing = draw_fing
 
    def process(self, img):
        # 1. inicjiacja zmiannych
        wave_points = []
        bbox = (0, 0, 0, 0)
        index_finger_pos = (0, 0)
        lm_list = []

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        # 2. sprawdzenie znalezenia reki
        if not results.multi_hand_landmarks:
            return None

        hand_landmarks = results.multi_hand_landmarks[0]
        h, w, _ = img.shape
        tip_ids = [4, 8, 12, 16, 20]

        # koordynaty palcew
        for id, lm in enumerate(hand_landmarks.landmark):
            if id in tip_ids:
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))

        if len(lm_list) < 5:
            return None

        # 3. obliczenia ramki i centrum
        x_list = [pt[0] for pt in lm_list]
        y_list = [pt[1] for pt in lm_list]
        x_min, x_max = min(x_list), max(x_list)
        y_min, y_max = min(y_list), max(y_list)
        xcenter, ycenter = (x_min + x_max) // 2, (y_min + y_max) // 2

        x_test, y_test = x_max - x_min, y_max - y_min
        prev_x_test, prev_y_test, _ = self.orient.update(x_test, y_test)

        x1, x2 = int(xcenter - prev_x_test // 2) - 10, int(xcenter + prev_x_test // 2) + 10
        y1, y2 = int(ycenter - prev_y_test // 2) - 10, int(ycenter + prev_y_test // 2) + 10
        bbox = (x1, y1, x2, y2)

        # sortowanie
        sorted_indices_x = sorted(range(5), key=lambda i: lm_list[i][0])
        
        index_finger_pos = lm_list[1] 

        # 4. wizualizacja
        if self.draw_lines:
            # lini miedzy palcow
            for i in range(4):
                cv2.line(img, lm_list[sorted_indices_x[i]], lm_list[sorted_indices_x[i+1]], (0, 255, 255), 2)

        if self.draw_fing:
            cv2.circle(img, index_finger_pos, 6, (0, 0, 255), -1)

        if self.draw_rect:
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        if self.draw_rect and self.draw_lines:
            cv2.line(img, (x1, ((y1 + y2) // 2)), lm_list[sorted_indices_x[0]], (0, 255, 255), 2) #бортики
            cv2.line(img, (x2, ((y1 + y2) // 2)), lm_list[sorted_indices_x[4]], (0, 255, 255), 2)

        # 5. koordynaty dla fal
        denom_x = (xcenter - x1) if (xcenter - x1) != 0 else 1
        denom_y = (ycenter - y2) if (ycenter - y2) != 0 else 1
        waveX = [(lm_list[i][0] - xcenter) / denom_x for i in sorted_indices_x]
        waveY = [(lm_list[i][1] - ycenter) / denom_y for i in sorted_indices_x]
        wave_points = [((waveX[i] + 1)/2, waveY[i]) for i in range(5)]
        wave_points.sort(key=lambda p: p[0])

        return wave_points, bbox, index_finger_pos, lm_list