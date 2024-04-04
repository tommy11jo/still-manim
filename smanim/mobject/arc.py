import numpy as np
from smanim.constants import ORIGIN, RIGHT, TAU, UP
from smanim.mobject.vmobject import VMobject
from smanim.typing import Point3D
from smanim.utils.space_ops import angle_from_vector


__all__ = ["Arc", "ArcBetweenPoints"]


class Arc(VMobject):
    def __init__(
        self,
        radius: float = 1.0,
        start_angle: float = 0.0,
        angle: float = TAU / 4,
        # Weakness: Setting num_components to a high value (instead of like 9) creates many more curves and a more accurate bounding polygon
        # This is necessary for realistic-looking intersection detection
        # FUTURE: Potentially do exact intersections in the future?
        num_components: float = 30,
        arc_center: Point3D = ORIGIN,
        **kwargs,
    ):
        if angle > TAU:
            raise ValueError("Arc angle must be <= 2*PI")
        self.radius = radius
        self.arc_center: Point3D = arc_center
        self.start_angle = start_angle
        self.angle = angle
        self.num_components = num_components
        super().__init__(is_closed=angle == TAU, **kwargs)

    def generate_points(self) -> None:  # override
        anchors = np.array(
            [
                np.cos(a) * RIGHT + np.sin(a) * UP
                for a in np.linspace(
                    self.start_angle,
                    self.start_angle + self.angle,
                    self.num_components,
                )
            ],
        )
        # Use tangent lines to generate control points
        d_theta = self.angle / (self.num_components - 1.0)
        tangent_vectors = np.zeros(anchors.shape)
        # Rotate all 90 degrees, via (x, y) -> (-y, x)
        tangent_vectors[:, 1] = anchors[:, 0]
        tangent_vectors[:, 0] = -anchors[:, 1]
        # For each anchor pair a1, a2, use tangent at a1 for first handle and tangent at a2 (in opposite direction) for second handle
        handles1 = anchors[:-1] + (d_theta / 3) * tangent_vectors[:-1]
        handles2 = anchors[1:] - (d_theta / 3) * tangent_vectors[1:]
        new_points = np.array(
            [
                p
                for pair in zip(anchors[:-1], handles1, handles2, anchors[1:])
                for p in pair
            ]
        )
        self.points = new_points

        self.scale(self.radius)
        self.shift(self.arc_center)

    def __repr__(self):
        class_name = self.__class__.__qualname__
        return f"{class_name}(radius={self.radius}, center={self.arc_center}, angle={self.angle})"


class ArcBetweenPoints(Arc):
    def __init__(
        self,
        start: Point3D,
        end: Point3D,
        angle: (
            float | None
        ) = None,  # in radians, note: use `angle` instead of `radius` when specified to help define the arc
        radius: float = 1.0,
        **kwargs,
    ):
        # The arc will be formed counter-clockwise from start to end along the circle
        self.start = np.array(start)
        self.end = np.array(end)
        chord_len = np.linalg.norm(self.end - self.start)
        chord_unit_dir = (self.end - self.start) / chord_len
        if not angle:
            angle = 2 * np.arcsin(chord_len / (2 * radius))
        midpoint = (self.start + self.end) / 2
        chord_to_center_len = (chord_len / 2) / np.tan(angle / 2)
        # perp to chord_unit_dir
        to_center_unit_dir = np.array([-chord_unit_dir[1], chord_unit_dir[0], 0])
        arc_center = midpoint + to_center_unit_dir * chord_to_center_len

        radius = chord_len / (2 * np.sin(angle / 2))

        center_to_start = self.start - arc_center
        start_angle = angle_from_vector(center_to_start)
        super().__init__(
            radius=radius,
            start_angle=start_angle,
            angle=angle,
            arc_center=arc_center,
            **kwargs,
        )
