# Geometry: directions
import numpy as np

from smanim.typing import Vector3


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

# Misc
DEFAULT_STROKE_WIDTH = 4.0
