import numpy as np
from smanim.constants import RIGHT, TAU, X_AXIS, Y_AXIS, Z_AXIS
from smanim.typing import Point2D, Point3D_Array, Vector3D
from smanim.utils.logger import logger


def to_pixel_coords(
    points: Point3D_Array,
    pw: float,
    ph: float,
    fw: float,
    fh: float,
    fc: Vector3D,
):
    if len(points) == 0:
        return []
    if not np.all(np.isfinite(points)):
        logger.warn("At least point is not finite. Using default (0, 0, 0).")
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
    if not any((axis == a).all() for a in (X_AXIS, Y_AXIS, Z_AXIS)):
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
    vector: Vector3D, angle: float, axis: np.ndarray = Z_AXIS
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
) -> Point2D | None:
    """Finds the line intersection using parametric equations.
    Returns the intersection point and the parametric scalar along the ray corresponding to the intersection.
    """
    seg_dir = segment_end - segment_start
    det_A = ray_direction[0] * seg_dir[1] - ray_direction[1] * seg_dir[0]
    if det_A == 0:
        return None, None

    diff = segment_start - ray_origin
    t = (diff[0] * seg_dir[1] - diff[1] * seg_dir[0]) / det_A
    u = (diff[0] * ray_direction[1] - diff[1] * ray_direction[0]) / det_A

    if t >= 0 and 0 <= u <= 1:
        return ray_origin + t * ray_direction, t
    else:
        return None, None
