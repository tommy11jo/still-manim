# Geometry: directions
import numpy as np

from smanim.typing import Vector3D

# Vector
ORIGIN: Vector3D = np.array((0.0, 0.0, 0.0))
CENTER = ORIGIN
"""The center of the coordinate system."""

UP: Vector3D = np.array((0.0, 1.0, 0.0))
"""One unit step in the positive Y direction."""

DOWN: Vector3D = np.array((0.0, -1.0, 0.0))
"""One unit step in the negative Y direction."""

RIGHT: Vector3D = np.array((1.0, 0.0, 0.0))
"""One unit step in the positive X direction."""

LEFT: Vector3D = np.array((-1.0, 0.0, 0.0))
"""One unit step in the negative X direction."""

IN: Vector3D = np.array((0.0, 0.0, -1.0))
"""One unit step in the negative Z direction."""

OUT: Vector3D = np.array((0.0, 0.0, 1.0))
"""One unit step in the positive Z direction."""
UL: Vector3D = UP + LEFT
"""One step up plus one step left."""

UR: Vector3D = UP + RIGHT
"""One step up plus one step right."""

DL: Vector3D = DOWN + LEFT
"""One step down plus one step left."""

DR: Vector3D = DOWN + RIGHT
"""One step down plus one step right."""

# Geometry: axes
X_AXIS: Vector3D = np.array((1.0, 0.0, 0.0))
Y_AXIS: Vector3D = np.array((0.0, 1.0, 0.0))
Z_AXIS: Vector3D = np.array((0.0, 0.0, 1.0))

# Mathematical
PI = np.pi
TAU = 2 * PI
DEGREES = TAU / 360
RADIANS = 360 / TAU

# Padding
# Default buffers (padding)
SMALL_BUFF = 0.1
MED_SMALL_BUFF = 0.25
MED_LARGE_BUFF = 0.5
LARGE_BUFF = 1
DEFAULT_MOBJECT_TO_EDGE_BUFFER = MED_LARGE_BUFF
DEFAULT_MOBJECT_TO_MOBJECT_BUFFER = MED_SMALL_BUFF

TEXT_X_PADDING = 0.02
TEXT_Y_PADDING = 0.02

# Misc
DEFAULT_STROKE_WIDTH = 4.0
DEFAULT_ARROW_TIP_LENGTH = 0.35
DEFAULT_DOT_RADIUS = 0.08
