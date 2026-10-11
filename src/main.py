#!/usr/bin/python3
import glob
import math
import os
import platform
import sys
import time
import traceback
from collections import deque

# Mute Linux ALSA audio driver warnings (must be set before pygame is used)
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import numpy as np
import pygame
import serial

import constants

# -----------------------------------------------------------------------------
# Tuning
# -----------------------------------------------------------------------------
NUM_OF_PLOT_POINTS = 100
FPS = 30

# Calibration
CAL_SAMPLES = 30          # samples wanted for the baseline (tara)
MIN_CAL_SAMPLES = 5       # fewer than this = calibration failed
CAL_TIMEOUT_SEC = 8.0     # time allowed to collect samples (after Arduino boot)

# Serial
BOOT_DELAY_SEC = 2.0      # Arduino usually resets when the port opens
RECONNECT_SEC = 2.0       # retry interval when the sensor is unplugged
NO_DATA_SEC = 2.0         # port is open but silent for this long = "No data"

# Signal processing
FILTER_ALPHA = 0.4                # smoothing per new sample (higher = faster response)
BASELINE_TAU_SEC = 0.7            # standing still fades out over a few seconds; flapping keeps it up
MIN_SCALE_SPAN = 20000.0
DECAY_RATE = 0.98                 # how fast the scale relaxes after a big push
DEAD_ZONE_FRAC = 0.02             # ignore effort below 2% of MIN_SCALE_SPAN
DEAD_ZONE = DEAD_ZONE_FRAC * MIN_SCALE_SPAN

LABEL_MAX_WIDTH_FRAC = 0.9        # calibration label may use 90% of screen width


class QuitRequested(Exception):
    """Raised from anywhere to leave the program cleanly."""


# -----------------------------------------------------------------------------
# Serial sensor
# -----------------------------------------------------------------------------
class Sensor:
    """Reads numeric lines from the Arduino, survives unplug/replug."""

    def __init__(self):
        self.ser = None
        self.opened_at = 0.0
        self.last_attempt = -1e9
        self.flushed = False
        self.skip = 0
        self.last_data = 0.0

    @staticmethod
    def candidate_ports():
        if platform.system() == "Windows":
            return ['COM3']
        ports = sorted(glob.glob('/dev/ttyUSB*')) + sorted(glob.glob('/dev/ttyACM*'))
        return ports or ['/dev/ttyUSB0']

    def connected(self):
        return self.ser is not None and self.ser.is_open

    def no_data(self):
        """True if the port is open but nothing has arrived for NO_DATA_SEC."""
        if not self.connected():
            return False
        since = max(self.last_data, self.opened_at + BOOT_DELAY_SEC)
        return time.time() - since > NO_DATA_SEC

    def _try_open(self):
        for port in self.candidate_ports():
            try:
                self.ser = serial.Serial(port, constants.BAUDRATE, timeout=0.01)
                self.opened_at = time.time()
                self.flushed = False
                self.last_data = 0.0
                print(f"Port {port} opened at {constants.BAUDRATE} baud.")
                return True
            except (serial.SerialException, OSError) as e:
                print(f"Could not open {port}: {e}")
        return False

    def close(self):
        if self.ser is not None:
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None

    def read_values(self):
        """Return a list of new float readings (possibly empty). Never blocks long."""
        now = time.time()

        if not self.connected():
            if now - self.last_attempt >= RECONNECT_SEC:
                self.last_attempt = now
                self._try_open()
            return []

        # Give the Arduino time to boot after the port opened
        if now - self.opened_at < BOOT_DELAY_SEC:
            return []

        values = []
        try:
            if not self.flushed:
                self.ser.reset_input_buffer()
                self.flushed = True
                self.skip = 2  # first line(s) after a flush may be partial
                return []

            while self.ser.in_waiting > 0:
                raw = self.ser.readline()
                if self.skip > 0:
                    self.skip -= 1
                    continue
                try:
                    val = float(raw.decode('utf-8', errors='ignore').strip())
                except ValueError:
                    continue  # bad line: skip only this one
                if not math.isfinite(val):
                    continue
                if val >= 2 ** 31:
                    val -= 2 ** 32  # undo uint32 wrap-around from the Arduino's offset
                values.append(val)
        except (serial.SerialException, OSError) as e:
            print(f"Sensor disconnected: {e}")
            self.close()
        if values:
            self.last_data = time.time()
        return values


# -----------------------------------------------------------------------------
# Application
# -----------------------------------------------------------------------------
class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('In case of problem call amir')

        info = pygame.display.Info()
        self.desktop_size = (info.current_w, info.current_h)
        self.fullscreen = constants.FULL_SCREEN
        self.clock = pygame.time.Clock()

        self.screen = self.open_display()
        self.raw_images = self.load_images()
        self.build_layout()

        self.sensor = Sensor()
        self.y_data = deque(maxlen=NUM_OF_PLOT_POINTS)
        self.tara = 0.0
        self.baseline = 0.0   # slowly follows the signal, so standing still fades out
        self.filtered = 0.0
        self.max_delta = MIN_SCALE_SPAN
        self.calibrated = False
        self.recalibrate = False

    # ---- display / layout --------------------------------------------------
    def open_display(self):
        if self.fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            w, h = self.desktop_size
            screen = pygame.display.set_mode((w * 4 // 5, h * 4 // 5))
        pygame.mouse.set_visible(constants.MOUSE_VISIBLE)
        return screen

    def load_images(self):
        images = []
        for j in range(constants.NUMBER_OF_IMAGES):
            path = f"{constants.RES_PATH}/image_{j}.png"
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Missing animation frame: {path}")
            images.append(pygame.image.load(path).convert_alpha())
        return images

    def build_layout(self):
        """Compute all positions from the real screen size."""
        w, h = self.screen.get_size()
        s = min(w / constants.SCREEN_W, h / constants.SCREEN_H)
        ox = (w - constants.SCREEN_W * s) / 2
        oy = (h - constants.SCREEN_H * s) / 2

        self.plot_rect = pygame.Rect(
            round(ox + constants.P_A_X * s), round(oy + constants.P_A_Y * s),
            round(constants.P_A_W * s), round(constants.P_A_H * s))
        self.frame_w = max(1, round(constants.P_A_F_T * s))
        self.line_w = max(1, round(constants.LINE_WIDTH * s))
        self.pic_x = ox + constants.PICTURE_X * s
        self.pic_y = oy + constants.PICTURE_Y * s
        self.dh = constants.DH * s

        if abs(s - 1.0) > 0.01:
            self.images = [
                pygame.transform.smoothscale(
                    img, (max(1, round(img.get_width() * s)), max(1, round(img.get_height() * s))))
                for img in self.raw_images]
        else:
            self.images = list(self.raw_images)

        self.label = self.fit_label(int(w * LABEL_MAX_WIDTH_FRAC))
        self.status_font = pygame.font.SysFont(constants.FONT_TYPE, max(12, round(40 * s)))

    def fit_label(self, max_width):
        """Render the calibration label, shrinking the font so it fits the screen."""
        size = constants.FONT_SIZE
        font = pygame.font.SysFont(constants.FONT_TYPE, size)
        surf = font.render(constants.LABEL, True, constants.FONT_COLOR)
        if surf.get_width() > max_width:
            size = max(12, int(size * max_width / surf.get_width()))
            font = pygame.font.SysFont(constants.FONT_TYPE, size)
            surf = font.render(constants.LABEL, True, constants.FONT_COLOR)
        return surf

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.screen = self.open_display()
        self.build_layout()

    # ---- events ------------------------------------------------------------
    def handle_events(self, calibrating=False):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise QuitRequested
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    raise QuitRequested
                if calibrating:
                    continue
                if event.key == pygame.K_t:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_r:
                    self.recalibrate = True

    # ---- calibration -------------------------------------------------------
    def draw_calibration(self):
        self.screen.fill(constants.SCREEN_COLOR)
        rect = self.label.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(self.label, rect)
        pygame.display.flip()

    def calibrate(self):
        """Measure the resting baseline (tara). Keeps the window responsive."""
        print("Calibrating Tara - please wait...")
        self.y_data.clear()
        self.max_delta = MIN_SCALE_SPAN

        samples = []
        deadline = time.time() + BOOT_DELAY_SEC + CAL_TIMEOUT_SEC
        while len(samples) < CAL_SAMPLES and time.time() < deadline:
            self.handle_events(calibrating=True)
            samples.extend(self.sensor.read_values())
            self.draw_calibration()
            self.clock.tick(60)  # also stops the loop from spinning at 100% CPU

        if len(samples) >= MIN_CAL_SAMPLES:
            self.tara = float(np.median(samples))  # median ignores outliers
            self.calibrated = True
            print(f"Baseline (Tara) calibrated to {self.tara} from {len(samples)} samples.")
        else:
            self.tara = 0.0
            self.calibrated = False
            print(f"Calibration failed ({len(samples)} samples). Will retry when the sensor is connected.")

        self.filtered = self.tara
        self.baseline = self.tara
        for _ in range(NUM_OF_PLOT_POINTS):
            self.y_data.append(0.0)  # history holds effort (movement), not raw values

    # ---- signal ------------------------------------------------------------
    def effort(self, value):
        """Movement = distance from the slowly adapting baseline, with a small dead zone."""
        e = abs(value - self.baseline)
        return 0.0 if e < DEAD_ZONE else e

    def update_scale(self, current_effort):
        if current_effort > self.max_delta:
            self.max_delta = current_effort
        else:
            self.max_delta = max(MIN_SCALE_SPAN, self.max_delta * DECAY_RATE)

    # ---- drawing -----------------------------------------------------------
    def draw_frame(self):
        screen = self.screen
        rect = self.plot_rect
        screen.fill(constants.SCREEN_COLOR)

        y_list = list(self.y_data)
        current_effort = y_list[-1]
        span = max(MIN_SCALE_SPAN, self.max_delta)

        # Plot area background + frame
        screen.fill(constants.P_A_C, rect)

        baseline_y = rect.y + rect.height * 0.70
        pixels_per_unit = (baseline_y - rect.y) / span
        dx = rect.width / (NUM_OF_PLOT_POINTS - 1)

        points = []
        for i, val in enumerate(y_list):
            py = baseline_y - val * pixels_per_unit
            py = max(rect.top, min(py, rect.bottom))
            points.append((rect.x + i * dx, py))
        if len(points) > 1:
            pygame.draw.lines(screen, constants.LINE_COLOR, False, points, self.line_w)

        pygame.draw.rect(screen, constants.P_A_F_C, rect, self.frame_w)

        # Dragon: frame and height follow the effort
        normalized = max(0.0, min(current_effort / span, 1.0))
        last = constants.NUMBER_OF_IMAGES - 1
        idx = max(0, min(int(normalized * last), last))
        offset = int(normalized * last * self.dh)
        screen.blit(self.images[idx], (self.pic_x, self.pic_y - offset))

        # Status message if the sensor is not there
        status = None
        if not self.sensor.connected():
            status = "Sensor not connected - retrying..."
        elif self.sensor.no_data():
            status = "No data from sensor - check HX711 wiring"
        if status:
            msg = self.status_font.render(status, True, constants.RED)
            screen.blit(msg, (10, screen.get_height() - msg.get_height() - 10))

        pygame.display.flip()

    # ---- main loop ---------------------------------------------------------
    def run(self):
        self.calibrate()
        dt = 1.0 / FPS

        while True:
            self.handle_events()

            if self.recalibrate or (
                    not self.calibrated and self.sensor.connected() and not self.sensor.no_data()):
                self.recalibrate = False
                self.calibrate()
                dt = 1.0 / FPS

            values = self.sensor.read_values()
            new_sample = bool(values) and self.calibrated
            if new_sample:
                latest = values[-1]  # one filter step per new reading
                self.filtered = FILTER_ALPHA * latest + (1.0 - FILTER_ALPHA) * self.filtered

            if self.calibrated:
                # The baseline slowly follows the signal: standing still fades to zero,
                # while fast movement (flapping) stays far from the baseline.
                self.baseline += (self.filtered - self.baseline) * (1.0 - math.exp(-dt / BASELINE_TAU_SEC))

            if new_sample:
                self.y_data.append(self.effort(self.filtered))

            self.update_scale(self.y_data[-1])
            self.draw_frame()
            dt = min(self.clock.tick(FPS) / 1000.0, 0.2)

    def close(self):
        self.sensor.close()
        pygame.quit()


def main():
    app = None
    try:
        app = App()
        app.run()
    except QuitRequested:
        pass
    finally:
        if app is not None:
            app.close()
        else:
            pygame.quit()
    print("Program exited cleanly.")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print("\n" + "=" * 50)
        print("CRASH DETECTED! ERROR DETAILS:")
        print("=" * 50)
        traceback.print_exc()
        print("=" * 50)
        sys.exit(1)