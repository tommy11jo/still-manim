from typing import List
import numpy as np
from smanim.mobject.arc import ArcBetweenPoints
from smanim.utils.bezier import interpolate
from smanim.utils.color import RED, ManimColor, has_default_colors_set
from smanim.constants import DL, DR, PI, UL, UR
from smanim.mobject.vmobject import VMobject
from smanim.typing import ManimFloat, Point3D, Point3D_Array
from smanim.utils.space_ops import regular_vertices

__all__ = ["Polygon", "Square", "Triangle", "RegularPolygon", "Rectangle"]


class Polygon(VMobject):
    def __init__(
        self,
        vertices: Point3D_Array,
        corner_radius: float = 0.0,
        default_stroke_color: ManimColor = RED,
        **kwargs,
    ):
        if not has_default_colors_set(**kwargs):
            kwargs["default_stroke_color"] = default_stroke_color
        self.vertices = vertices
        self.corner_radius = corner_radius
        super().__init__(**kwargs)
        if corner_radius > 0:
            self.round_corners(corner_radius)

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

    # This will no longer work if corners get rounded
    def get_vertices(self):
        return self.get_start_anchors()

    def __repr__(self):
        class_name = self.__class__.__qualname__
        vertices = self.get_vertices()
        clipped_pts = vertices if len(vertices) < 6 else vertices[:3] + vertices[-3:]
        return (
            f'{class_name}(vertices={" ,".join([f"Point({pt})" for pt in clipped_pts])}'
        )

    def round_corners(self, corner_radius: float) -> None:
        """Applies surgery to the polygon, reducing the existing lines and inserting the arcs at the corners.
        Assumes each side is a single line made of 4 bezier points and that the lines in self.points correspond to the vertices in self.vertices
        """
        if corner_radius == 0:
            return
        new_points = []
        quads = self.get_points_in_quads(self.points)
        quads_behind = np.roll(quads, -1, axis=0)
        # first step: excise unwanted parts of existing lines
        # second step: fill in corners with arcs
        # for quad1, quad2 in zip(quads, quads_ahead):
        # l1_dir = quad1[-1] - quad1[0]
        new_quads = []
        # for quad, next_quad in zip(quads_behind, quads):
        for quad in quads:
            l1_vec = quad[-1] - quad[0]
            l1_norm = np.linalg.norm(l1_vec)
            l1_vec_norm = l1_vec / l1_norm
            if l1_norm < 2 * corner_radius:
                corner_radius = np.linalg.norm(l1_vec) / 2

            new_l1_start = quad[0] + l1_vec_norm * corner_radius
            new_l1_end = quad[-1] - l1_vec_norm * corner_radius

            bezier_pts = [
                interpolate(new_l1_start, new_l1_end, a)
                for a in np.linspace(0, 1, VMobject.points_per_curve)
            ]
            if new_quads:
                prev_end = new_quads[-1][-1]
                cur_start = bezier_pts[0]
                arc = ArcBetweenPoints(prev_end, cur_start, angle=PI / 2)

                new_quads.extend(arc.get_points_in_quads(arc.points))
                new_quads.append(np.array(bezier_pts))
            else:
                new_quads.append(np.array(bezier_pts))
        prev_end = new_quads[-1][-1]
        cur_start = new_quads[0][0]
        arc = ArcBetweenPoints(prev_end, cur_start, angle=PI / 2, stroke_width=1)
        new_quads.extend(arc.get_points_in_quads(arc.points))

        quads_behind = np.roll(new_quads, 1, axis=0)
        for quad1, quad2 in zip(new_quads, quads_behind):
            new_start = quad1[-1]
            new_end = quad2[0]
            bezier_pts = [
                interpolate(new_start, new_end, a)
                for a in np.linspace(0, 1, VMobject.points_per_curve)
            ]
            new_points.extend(quad1)
            new_points.extend(bezier_pts)

        self.points = np.array(new_points)


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
