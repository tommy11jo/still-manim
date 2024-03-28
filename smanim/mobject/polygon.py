from typing import List
import numpy as np
from smanim.utils.bezier import interpolate
from smanim.utils.color import RED, WHITE, ManimColor
from smanim.constants import DL, DR, UL, UR
from smanim.mobject.vmobject import VMobject
from smanim.typing import Point3D, Point3D_Array


class Polygon(VMobject):
    def __init__(self, vertices: Point3D_Array, color: ManimColor = RED, **kwargs):
        self.vertices = vertices
        super().__init__(color=color, **kwargs)

    def generate_points(self) -> Point3D_Array:
        """Override to generate points by interpolating between each pair of vertices"""
        points: List[Point3D] = []
        for start, end in zip(self.vertices, self.vertices[1:]):
            bezier_pts = [
                interpolate(start, end, a)
                for a in np.linspace(0, 1, VMobject.points_per_curve)
            ]
            points.extend(bezier_pts)
        return np.array(points)

    def get_vertices(self):
        return self.vertices
        # return self.get_start_anchors()

    def __repr__(self):
        class_name = self.__class__.__qualname__
        vertices = self.get_vertices()
        clipped_pts = vertices if len(vertices) < 6 else vertices[:3] + vertices[-3:]
        return (
            f'{class_name}(vertices={" ,".join([f"Point({pt})" for pt in clipped_pts])}'
        )


class Rectangle(Polygon):
    def __init__(
        self, width: int = 2, height: int = 1, color: ManimColor = WHITE, **kwargs
    ):
        scalar = np.array([width / 2, height / 2, 1])
        super().__init__(
            [UR * scalar, UL * scalar, DL * scalar, DR * scalar], color=color, **kwargs
        )
        self.width = width
        self.height = height

    def __repr__(self):
        class_name = self.__class__.__qualname__
        return f"{class_name}(width={self.width}, height={self.height})"


class Square(Polygon):
    def __init__(self, side_length: int = 1, color: ManimColor = WHITE, **kwargs):
        super().__init__(
            [UR * side_length, UL * side_length, DL * side_length, DR * side_length],
            color=color,
            **kwargs,
        )
        self.side_length = side_length

    def __repr__(self):
        class_name = self.__class__.__qualname__
        return f"{class_name}(side_length={self.side_length})"


# TODO: RegularPolygon and Triangle
