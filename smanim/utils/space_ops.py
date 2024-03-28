import numpy as np
from smanim.typing import Point3D_Array, Vector3
from smanim.utils.logger import logger


def to_pixel_coords(
    points: Point3D_Array,
    pw: float,
    ph: float,
    fw: float,
    fh: float,
    fc: Vector3,
):
    if not np.all(np.isfinite(points)):
        logger.warn("At least point is not finite. Using default (0, 0, 0).")
        points = np.zeros((1, 3))
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
