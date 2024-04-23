# Geometry: directions
import numpy as np

from smanim.typing import Vector3

# Vector
ORIGIN: Vector3 = np.array((0.0, 0.0, 0.0))
"""The center of the coordinate system."""

UP: Vector3 = np.array((0.0, 1.0, 0.0))
"""One unit step in the positive Y direction."""

DOWN: Vector3 = np.array((0.0, -1.0, 0.0))
"""One unit step in the negative Y direction."""

RIGHT: Vector3 = np.array((1.0, 0.0, 0.0))
"""One unit step in the positive X direction."""

LEFT: Vector3 = np.array((-1.0, 0.0, 0.0))
"""One unit step in the negative X direction."""

IN: Vector3 = np.array((0.0, 0.0, -1.0))
"""One unit step in the negative Z direction."""

OUT: Vector3 = np.array((0.0, 0.0, 1.0))
"""One unit step in the positive Z direction."""
UL: Vector3 = UP + LEFT
"""One step up plus one step left."""

UR: Vector3 = UP + RIGHT
"""One step up plus one step right."""

DL: Vector3 = DOWN + LEFT
"""One step down plus one step left."""

DR: Vector3 = DOWN + RIGHT
"""One step down plus one step right."""

# Geometry: axes
X_AXIS: Vector3 = np.array((1.0, 0.0, 0.0))
Y_AXIS: Vector3 = np.array((0.0, 1.0, 0.0))
Z_AXIS: Vector3 = np.array((0.0, 0.0, 1.0))

# Mathematical
PI = np.pi
TAU = 2 * PI
DEGREES = TAU / 360
RADIANS = 360 / TAU

# Padding
TINY_BUFF = 0.03
SMALL_BUFF = 0.1
MED_SMALL_BUFF = 0.25
MED_LARGE_BUFF = 0.5
LARGE_BUFF = 1
DEFAULT_MOBJECT_TO_EDGE_BUFFER = MED_LARGE_BUFF
DEFAULT_MOBJECT_TO_MOBJECT_BUFFER = SMALL_BUFF

# Text
TEXT_X_PADDING = 0.02
TEXT_Y_PADDING = 0.02
H1_FONT_SIZE = 40
H2_FONT_SIZE = 30
H3_FONT_SIZE = 24
DEFAULT_FONT_SIZE = 20

# Layering
Z_INDEX_MIN = -2147483648

# Resolutions
LOW_RES = 72  # 72 pixels per unit
MEDIUM_RES = 90  # 90 pixels per unit
HIGH_RES = 120  # 120 pixels per unit

# Misc
DEFAULT_STROKE_WIDTH = 4.0
DEFAULT_ARROW_TIP_LENGTH = 0.35
DEFAULT_DOT_RADIUS = 0.08
