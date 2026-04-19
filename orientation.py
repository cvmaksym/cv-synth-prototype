import time

class OrientationSmoother:
    def __init__(self):
        self.current_orientation = None
        self.orientation_change_time = None

        self.prev_x = None
        self.prev_y = None
        self.target_x = None
        self.target_y = None

    def detect_orientation(self, x_test, y_test):
        return "portrait" if y_test > x_test else "landscape"

    def update(self, x_test, y_test):
        detected = self.detect_orientation(x_test, y_test)
        now = time.time()
        changed = False

        # sprawdzenie zmiany orientacji
        if detected != self.current_orientation:
            if self.orientation_change_time is None:
                self.orientation_change_time = now
            elif now - self.orientation_change_time >= 0.1:
                self.current_orientation = detected
                self.orientation_change_time = None
                changed = True
        else:
            self.orientation_change_time = None

        # rozrachunek
        if changed:
            if self.current_orientation == "portrait":
                self.target_x = (y_test / 9) * 16
                self.target_y = y_test
            else:
                self.target_x = x_test
                self.target_y = (x_test / 16) * 9

            if self.prev_x is None:
                self.prev_x = self.target_x
            if self.prev_y is None:
                self.prev_y = self.target_y

        else:
            if self.current_orientation == "portrait":
                self.target_x = (y_test / 9) * 16
                self.target_y = y_test
            else:
                self.target_x = x_test
                self.target_y = (x_test / 16) * 9

            self.prev_x = self.target_x
            self.prev_y = self.target_y

        # plynne zblizenie
        if changed:
            k = 0.2
            self.prev_x += (self.target_x - self.prev_x) * k
            self.prev_y += (self.target_y - self.prev_y) * k

        return self.prev_x, self.prev_y, changed