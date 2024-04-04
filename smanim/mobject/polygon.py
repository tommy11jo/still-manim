from typing import List
from typing_extensions import Self
import numpy as np
from smanim.mobject.arc import ArcBetweenPoints
from smanim.utils.bezier import interpolate
from smanim.utils.color import RED, ManimColor, has_default_colors_set
from smanim.constants import DL, DR, ORIGIN, OUT, PI, UL, UR
from smanim.mobject.vmobject import VMobject
from smanim.typing import ManimFloat, Point3D, Point3D_Array, QuadArray_Point3D, Vector3
from smanim.utils.space_ops import regular_vertices
from smanim.utils.logger import log

__all__ = [
    "Polygon",
    "Square",
    "Triangle",
    "RegularPolygon",
    "Rectangle",
]


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
        self._vertices = np.array(vertices)
        self.corner_radius = corner_radius
        super().__init__(**kwargs)
        if corner_radius > 0:
            self.round_corners(corner_radius)
            self.rounded = True

    def generate_points(self) -> None:
        """Override to generate points by interpolating between each pair of vertices"""
        points: List[Point3D] = []
        vertices_behind = np.roll(self.vertices, -1, axis=0)
        for start, end in zip(self.vertices, vertices_behind):
            bezier_pts = [
                interpolate(start, end, a)
                for a in np.linspace(0, 1, VMobject.points_per_curve)
            ]
            points.extend(bezier_pts)
        self.points = np.array(points, dtype=ManimFloat)

    @property
    def vertices(self) -> Point3D_Array:
        return self._vertices

    @vertices.setter
    def vertices(self, value: Point3D_Array) -> None:
        self._vertices = value

    def reset_points_from_vertices(self, new_vertices: Point3D_Array) -> None:
        self.vertices = np.array(new_vertices)
        self.generate_points()
        if self.corner_radius > 0:
            self.round_corners(self.corner_radius)

    def __repr__(self) -> str:
        class_name = self.__class__.__qualname__
        vertices = self.vertices
        clipped_pts = vertices if len(vertices) < 6 else vertices[:3] + vertices[-3:]
        return (
            f'{class_name}(vertices={" ,".join([f"Point({pt})" for pt in clipped_pts])}'
        )

    def round_corners(self, radius: float) -> None:
        """Applies surgery to the polygon, reducing the existing lines and inserting the arcs at the corners.
        Assumes each side is a single line made of 4 bezier points and that the lines in self.points correspond to the vertices in self.vertices
        Constraint: Only handles convex shapes with counter-clockwise point orientation. In the future, if concave is needed, accept radius list and use radius sign to determine concavity.
        """
        if radius == 0:
            return
        quads = self.get_points_in_quads(self.points)
        new_quads = []

        def _arc_from_quads(
            quad1: QuadArray_Point3D, quad2: QuadArray_Point3D
        ) -> ArcBetweenPoints:
            prev_end = quad1[-1]
            prev_start = quad1[0]
            cur_start = quad2[0]
            cur_end = quad2[-1]
            prev, cur = prev_end - prev_start, cur_end - cur_start
            angle = np.arccos(
                np.dot(prev, cur) / (np.linalg.norm(prev) * np.linalg.norm(cur))
            )
            arc = ArcBetweenPoints(prev_end, cur_start, angle=angle)
            return arc

        for quad in quads:
            l1_vec = quad[-1] - quad[0]
            l1_norm = np.linalg.norm(l1_vec)
            l1_vec_norm = l1_vec / l1_norm
            if l1_norm < 2 * radius:
                # radius = np.linalg.norm(l1_vec) / 2 - 0.01
                log.warning("Corner radius too big, using unrounded corners.")
                return

            new_l1_start = quad[0] + l1_vec_norm * radius
            new_l1_end = quad[-1] - l1_vec_norm * radius

            bezier_pts = [
                interpolate(new_l1_start, new_l1_end, a)
                for a in np.linspace(0, 1, VMobject.points_per_curve)
            ]
            if new_quads:
                arc = _arc_from_quads(new_quads[-1], bezier_pts)

                new_quads.extend(arc.get_points_in_quads(arc.points))
                new_quads.append(np.array(bezier_pts))
            else:
                new_quads.append(np.array(bezier_pts))
        arc = _arc_from_quads(new_quads[-1], new_quads[0])

        new_quads.extend(arc.get_points_in_quads(arc.points))
        self.points = np.concatenate(np.array(new_quads), axis=0)
        self.rounded = True

    # Override the core transformations to keep vertices updated
    def rotate(
        self,
        angle: float = PI / 4,
        axis: Vector3 = OUT,
        about_point: Point3D | None = None,
    ) -> Self:
        self.vertices = super().rotate_points(self.vertices, angle, axis, about_point)
        self.points = super().rotate_points(self.points, angle, axis, about_point)
        for mob in self.submobjects:
            mob.rotate(angle, axis, about_point)
        return self

    def scale(self, factor: float, about_point: Point3D | None = ORIGIN) -> Self:
        self.vertices = super().scale_points(self.vertices, factor, about_point)
        self.points = super().scale_points(self.points, factor, about_point)
        for mob in self.submobjects:
            mob.scale(factor, about_point)
        return self

    def stretch(self, factor: float, dim: int) -> Self:
        self.vertices = super().stretch_points(self.vertices, factor, dim)
        self.points = super().stretch_points(self.points, factor, dim)
        for mob in self.submobjects:
            mob.stretch(factor, dim)
        return self

    def shift(self, vector: Vector3) -> Self:
        self.vertices = super().shift_points(self.vertices, vector)
        self.points = super().shift_points(self.points, vector)
        for mob in self.submobjects:
            mob.shift(vector)
        return self


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
