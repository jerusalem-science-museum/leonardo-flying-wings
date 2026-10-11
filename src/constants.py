import os.path

RES_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))), 'res', 'dragon'))

MOUSE_VISIBLE = False

FONT_TYPE = 'Comic Sans MS'
FONT_SIZE = 80
FONT_COLOR = (255, 0, 0)
LABEL = 'Calibration - DONT stand on plate'
LABEL_X_Y = (100, 100)

LINE_WIDTH = 3  # Line width

FULL_SCREEN = True  # True to toggle to full screen

NUMBER_OF_IMAGES = 6  # Number of frames for animation

SCREEN_W = 1920  # Corrected from 1980 to standard Full HD width
SCREEN_H = 1080
IMAGE_X_Y = (0, 0)
IMAGE_W = 600
IMAGE_H = 1000

PICTURE_X = 0  # Upper left image X position
PICTURE_Y = 400  # Upper left image Y position
DH = 40  # Delta Y for up/dn image according to value

# Plot Area configuration
P_A_X = 600
P_A_Y = 50
P_A_W = 700
P_A_H = 650
P_A_F_C = (0, 0, 0)
P_A_F_T = 3
P_A_C = (255, 255, 255)

BAUDRATE = 115200  # Serial communication baudrate (corrected spelling)
LINE_COLOR = (0, 0, 255)
SCREEN_COLOR = (155, 155, 100)
SURFACE_COLOR = (155, 155, 100)
IMAGE_BK_COLOR = (155, 155, 100)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
