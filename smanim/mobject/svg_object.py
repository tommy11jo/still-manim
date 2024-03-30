from typing import List
import numpy as np
from smanim.mobject.vmobject import VMobject
import svgelements as se

from smanim.typing import ManimFloat, Point3D


def _to_3d(x: float, y: float) -> np.ndarray:
    return np.array([x, y, 0.0])


class VMobjectFromSVGPath(VMobject):
    """Extracts points from the given SVG path to use the "manim intermediate repr" for things like rotation."""

    def __init__(self, path_obj: se.Path, **kwargs):
        self.path_obj = path_obj
        super().__init__(**kwargs)

    def generate_points(self) -> None:  # override
        if VMobject.points_per_curve != 4:
            raise ValueError("`points_per_curve` must be 4")

        all_points: List[Point3D] = []
        last_move = None
        curve_start = None

        # use list instead of numpy array to avoid O(n^2) behavior of np.append() for complex paths
        def move_pen(pt):
            nonlocal last_move, curve_start
            last_move = pt
            if curve_start is None:
                curve_start = last_move

        def add_cubic(start, cp1, cp2, end):
            nonlocal all_points
            assert len(all_points) % 4 == 0, len(all_points)
            all_points += [start, cp1, cp2, end]
            move_pen(end)

        def add_quad(start, cp, end):
            add_cubic(start, (start + cp + cp) / 3, (cp + cp + end) / 3, end)
            move_pen(end)

        def add_line(start, end):
            add_cubic(start, (start + start + end) / 3, (start + end + end) / 3, end)
            move_pen(end)

        for segment in self.path_obj:
            segment_class = segment.__class__
            if segment_class == se.Move:
                move_pen(_to_3d(*segment.end))
            elif segment_class == se.Line:
                add_line(last_move, _to_3d(*segment.end))
            elif segment_class == se.QuadraticBezier:
                add_quad(
                    last_move,
                    _to_3d(*segment.control),
                    _to_3d(*segment.end),
                )
            elif segment_class == se.CubicBezier:
                add_cubic(
                    last_move,
                    _to_3d(*segment.control1),
                    _to_3d(*segment.control2),
                    _to_3d(*segment.end),
                )
            elif segment_class == se.Close:
                add_line(last_move, curve_start)
                curve_start = None
            else:
                raise AssertionError(f"Not implemented: {segment_class}")
        self.points = np.array(all_points, dtype=ManimFloat)
