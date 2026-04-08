from manim import *

# DESIGN TOKENS
BG_COLOR = "#0a1224"
PRIMARY_COLOR = BLUE_C
SECONDARY_COLOR = YELLOW_C
ACCENT_COLOR = GREEN_C
TEXT_COLOR = WHITE

TITLE_FONT_SIZE = 48
BODY_FONT_SIZE = 32
SMALL_FONT_SIZE = 24

SAFE_WIDTH = config.frame_width - 2
SAFE_HEIGHT = config.frame_height - 2

# TIMINGS
SCENE_DURATION = 8 # seconds
TRANSITION_TIME = 0.5

def get_title(text, color=PRIMARY_COLOR):
    t = Text(text, font_size=TITLE_FONT_SIZE, color=color, weight=BOLD)
    if t.width > SAFE_WIDTH:
        t.scale_to_fit_width(SAFE_WIDTH)
    return t

def get_body(text, color=TEXT_COLOR):
    t = Text(text, font_size=BODY_FONT_SIZE, color=color)
    if t.width > SAFE_WIDTH:
        t.scale_to_fit_width(SAFE_WIDTH)
    return t

def apply_safe_layout(mobj):
    if mobj.width > SAFE_WIDTH:
        mobj.scale_to_fit_width(SAFE_WIDTH)
    if mobj.height > SAFE_HEIGHT:
        mobj.scale_to_fit_height(SAFE_HEIGHT)
    return mobj
