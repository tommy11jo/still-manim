from smanim.typing import Point3D


def interpolate(
    start: int | float | Point3D, end: int | float | Point3D, alpha: float | Point3D
) -> float | Point3D:
    return (1 - alpha) * start + alpha * end
