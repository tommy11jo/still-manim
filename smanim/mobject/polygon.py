from typing import List
import numpy as np
from smanim.utils.bezier import interpolate
from smanim.utils.color import RED, ManimColor
from smanim.constants import DL, DR, UL, UR
from smanim.mobject.vmobject import VMobject
from smanim.typing import ManimFloat, Point3D, Point3D_Array
from smanim.utils.space_ops import regular_vertices


class Polygon(VMobject):
    def __init__(
        self, vertices: Point3D_Array, default_stroke_color: ManimColor = RED, **kwargs
    ):
        self.vertices = vertices
        super().__init__(default_stroke_color=default_stroke_color, **kwargs)

    def generate_points(self) -> None:
        """Override to generate points by interpolating between each pair of vertices"""
        points: List[Point3D] = []
        vertices_ahead = np.roll(self.vertices, -1, axis=0)
        for start, end in zip(self.vertices, vertices_ahead):
            bezier_pts = [
                interpolate(start, end, a)
                for a in np.linspace(0, 1, VMobject.points_per_curve)
            ]
            points.extend(bezier_pts)
        self.points = np.array(points, dtype=ManimFloat)

    def get_vertices(self):
        return self.get_start_anchors()

    def __repr__(self):
        class_name = self.__class__.__qualname__
        vertices = self.get_vertices()
        clipped_pts = vertices if len(vertices) < 6 else vertices[:3] + vertices[-3:]
        return (
            f'{class_name}(vertices={" ,".join([f"Point({pt})" for pt in clipped_pts])}'
        )


class Rectangle(Polygon):
    def __init__(self, width: int = 2, height: int = 1, **kwargs):
        scalar = np.array([width / 2, height / 2, 1])
        super().__init__(
            [UR * scalar, UL * scalar, DL * scalar, DR * scalar],
            **kwargs,
        )

    def __repr__(self):
        class_name = self.__class__.__qualname__
        return f"{class_name}(width={self.width}, height={self.height})"


class Square(Polygon):
    def __init__(self, side_length: int = 1, **kwargs):
        super().__init__(
            [UR * side_length, UL * side_length, DL * side_length, DR * side_length],
            **kwargs,
        )
        self.side_length = side_length

    def __repr__(self):
        class_name = self.__class__.__qualname__
        return f"{class_name}(side_length={self.side_length})"


class RegularPolygon(Polygon):
    def __init__(
        self, n: int = 6, radius: int = 1, start_angle: int | None = None, **kwargs
    ):
        vertices = regular_vertices(n, radius, start_angle)
        super().__init__(vertices, **kwargs)
        self.n = n
        self.radius = radius
        # angle in radians
        self.start_angle = start_angle


class Triangle(RegularPolygon):
    def __init__(self, **kwargs) -> None:
        super().__init__(n=3, **kwargs)
