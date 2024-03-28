from typing import List, Tuple

import numpy as np
from smanim.constants import DEFAULT_STROKE_WIDTH
from smanim.utils.color import WHITE, ManimColor
from smanim.mobject.mobject import Mobject
from smanim.typing import Point3D, Point3D_Array


# Note: text is not a VMobject, it's a non-vectorized SVG el
class VMobject(Mobject):
    "base class for all objects represented by a path of bezier curves, with strokes or fills"
    points_per_curve = 4

    def __init__(
        self,
        color: ManimColor | None = WHITE,
        stroke_width: float = DEFAULT_STROKE_WIDTH,
        stroke_color: ManimColor | None = None,
        stroke_opacity: float = 1.0,
        fill_color: ManimColor | None = None,
        fill_opacity: float = 0.0,
    ):
        super().__init__()

        self.fill_color = fill_color if fill_color else color
        self.fill_opacity = fill_opacity
        self.stroke_color = stroke_color if stroke_color else color
        self.stroke_opacity = stroke_opacity
        self.stroke_width = stroke_width

    def get_start_anchors(self) -> Point3D_Array:
        return self.points[:: self.points_per_curve]

    def get_end_anchors(self) -> Point3D_Array:
        return self.points[self.points_per_curve - 1 :: self.points_per_curve]

    def get_points_in_quads(
        self, points: Point3D_Array
    ) -> List[Tuple[Point3D, Point3D, Point3D, Point3D]]:
        assert len(points) % 4 == 0, "Points should be divisible by 4"
        return [tuple(points[i : i + 4]) for i in range(0, len(points), 4)]

    def append_points(self, new_points: Point3D_Array):
        if len(self.points) == 0:
            self.points = new_points
        else:
            self.points = np.append(self.points, new_points, axis=0)
