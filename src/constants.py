import os.path

TIME_FOR_PLOT_PER_SEC = 300 # time (sec) for plotupadte rate calculation
NUM_OF_PLOT_POINTS = 100 # number of point to plot

NUM_OF_UPDATE_POINT = 3 #number of points updated befour move plot 

TIME_SAFE_MARGINE = 1.1 #aditional time to make sure  


RES_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))), 'res', 'dragon'))


MOUSE_VISIBE = False
HALF_SCALE_UP = 200000.0 # half scaLe mean +
HALF_SCALE_DN = 100000.0 # half scaLe mean +


FONT_TYPE = 'Comic Sans MS'
FONT_SIZE = 120
FONT_COLOR = (255,0,0)
LABEL = 'Calibration - DONT stand on plate'
LABEL_X_Y = (100,100)


SCALE_FACTOR = -2 # Y axis scale factor

SCALE_FACTOR_UP = -2 # Y axis scale factor

SCALE_FACTOR_DN = -1.1 # Y axis scale factor 

LINE_WIDTH = 3 # line width

FULL_SCREEN = True # False # true to toggle to full screen

NUMBER_OF_IMAGES = 6 # number of frames for animation


SCREEN_W = 1980
SCREEN_H = 1080
IMAGE_X_Y = (0,0)
#IMAGE_X = 0
#IMAGE_Y = 0
IMAGE_W = 600
IMAGE_H = 1000

PICTURE_X = 0 # upper left image X position
PICTURE_Y = 400 # upper left image Y position
DH = 40 # delta Y for up/dn image acording to value

#P_A = plot area
# F = frame, C = color, T = thick
P_A_X = 600
P_A_Y = 50
P_A_W = 700
P_A_H = 650
P_A_F_C = (0,0,0)
P_A_F_T = 3
P_A_C = (255,255,255)

#SCREEN_W = 600
#SCREEN_H = 400
#IMAGE_W = 600
#IMAGE_H = 400

BOUDRATE = 57600  # serial comunication boudrate
#BOUDRATE = 57600  # serial comunication boudrate
LINE_COLOR  = (0,0,255)
SCREEN_COLOR = (155,155,100)
SURFACE_COLOR = (155,155,100)
IMAGE_BK_COLOR = (155,155,100)
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)
