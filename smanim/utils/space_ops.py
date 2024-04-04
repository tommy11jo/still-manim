from typing import Tuple
import numpy as np
from smanim.constants import RIGHT, TAU, X_AXIS, Y_AXIS, Z_AXIS
from smanim.typing import Point2D, Point3D_Array, Vector3
from smanim.utils.logger import log


# pixel scalar => manim scalar
def to_pixel_len(scalar: float, pw: float, fw: float):
    return scalar * (pw / fw)


# manim scalar => pixel scalar
def to_manim_len(scalar: float, pw: float, fw: float):
    return scalar * (fw / pw)


def to_pixel_coords(
    points: Point3D_Array,
    pw: float,
    ph: float,
    fw: float,
    fh: float,
    fc: Vector3,
):
    if len(points) == 0:
        return []
    if not np.all(np.isfinite(points)):
        log.warn("At least point is not finite. Using default (0, 0, 0).")
        points = np.zeros((1, 3))
    points = points.copy()
    # assume points are 2D so last dimesion z is unused in [x, y, z]
    points[:, -1] = 1
    # instead of using a matrix within cairo or canvas

    coord_mat = np.array(
        [
            [pw / fw, 0, (pw / 2) - fc[0] * (pw / fw)],
            [0, -(ph / fh), (ph / 2) + fc[1] * (ph / fh)],
        ]
    )
    # (N x 3) @ (3 x 2) = (N x 2)
    points = points @ coord_mat.T
    return points


def rotation_matrix(angle_in_radians: float, axis: np.ndarray) -> np.ndarray:
    """Counter-clockwise rotation"""
    if not any(np.array_equal(axis, a) for a in (X_AXIS, Y_AXIS, Z_AXIS)):
        raise ValueError("Axis must be one of (X_AXIS, Y_AXIS, Z_AXIS)")

    c = np.cos(angle_in_radians)
    s = np.sin(angle_in_radians)
    t = 1 - c
    x, y, z = axis

    return np.array(
        [
            [t * x * x + c, t * x * y - z * s, t * x * z + y * s],
            [t * x * y + z * s, t * y * y + c, t * y * z - x * s],
            [t * x * z - y * s, t * y * z + x * s, t * z * z + c],
        ]
    )


def rotate_vector(
    vector: Vector3, angle: float, axis: np.ndarray = Z_AXIS
) -> np.ndarray:
    """Counter-clockwise rotation"""
    if len(vector) > 3:
        raise ValueError("Vector must have the correct dimensions.")
    return rotation_matrix(angle, axis) @ vector


def compass_directions(n: int = 4, start_vect: np.ndarray = RIGHT) -> np.ndarray:
    """Finds the cardinal directions using tau."""
    angle = TAU / n
    return np.array([rotate_vector(start_vect, k * angle) for k in range(n)])


def regular_vertices(
    n: int, radius: float = 1, start_angle: float | None = None
) -> np.ndarray:
    """Generates regularly spaced vertices around a circle centered at the origin in the counter-clockwise direction."""

    if start_angle is None:
        if n % 2 == 0:
            start_angle = 0
        else:
            start_angle = TAU / 4

    start_vector = rotate_vector(RIGHT * radius, start_angle)
    vertices = compass_directions(n, start_vector)

    return vertices


def line_intersect(
    ray_origin: Point2D,
    ray_direction: Point2D,
    segment_start: Point2D,
    segment_end: Point2D,
) -> Tuple[Point2D, float] | Tuple[None, None]:
    """Finds the line intersection using parametric equations.
    Returns the intersection point and the parametric scalar along the ray corresponding to the intersection.
    """
    seg_dir = segment_end - segment_start

    det_A = np.cross(ray_direction, seg_dir)
    if det_A == 0:
        return None, None

    diff = segment_start - ray_origin
    t = np.cross(diff, seg_dir) / det_A
    u = np.cross(diff, ray_direction) / det_A

    if t >= 0 and 0 <= u <= 1:
        return ray_origin + t * ray_direction, t
    else:
        return None, None


def angle_from_vector(vector3: Vector3):
    """Returns the angle from the vector, on [0, 2*PI]"""
    dir_x, dir_y = vector3[:2]
    angle = np.arctan2(dir_y, dir_x)
    if angle < 0:
        angle += TAU
    return angle
