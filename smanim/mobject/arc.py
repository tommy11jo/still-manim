import numpy as np
from smanim.constants import DEFAULT_DOT_RADIUS, ORIGIN, RIGHT, TAU, UP
from smanim.mobject.vmobject import VMobject
from smanim.typing import Point3D
from smanim.utils.color import RED, WHITE, ManimColor


class Arc(VMobject):
    def __init__(
        self,
        radius: float = 1.0,
        start_angle: float = 0.0,
        angle: float = TAU / 4,
        num_components: float = 9,
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

        self.scale(self.radius, about_point=ORIGIN)
        self.shift(self.arc_center)


class ArcBetweenPoints(Arc):
    def __init__(
        self,
        start: Point3D,
        end: Point3D,
        # angle: float = TAU / 4, # Not sure when this would be useful?
        radius: float = 1.0,
        **kwargs,
    ):
        # The arc will be formed counter-clockwise from start to end along the circle
        self.start = start
        self.end = end
        self.radius = radius

        start_x, start_y = start[:2]
        start_angle = np.arctan2(start_y, start_x)
        start_angle = start_angle if start_angle >= 0 else start_angle + TAU
        end_x, end_y = end[:2]
        end_angle = np.arctan2(end_y, end_x)
        end_angle = end_angle if end_angle >= 0 else end_angle + TAU

        super().__init__(
            radius=radius,
            start_angle=start_angle,
            angle=end_angle - start_angle,
            **kwargs,
        )


class Circle(Arc):
    def __init__(
        self,
        radius: float = 1.0,
        default_stroke_color: ManimColor = RED,
        **kwargs,
    ) -> None:
        super().__init__(
            radius=radius,
            start_angle=0,
            angle=TAU,
            default_stroke_color=default_stroke_color,
            **kwargs,
        )


class Dot(Circle):
    def __init__(
        self,
        point: Point3D = ORIGIN,
        radius: float = DEFAULT_DOT_RADIUS,
        default_fill_color: ManimColor = WHITE,
        **kwargs,
    ) -> None:
        super().__init__(
            arc_center=point,
            radius=radius,
            default_fill_color=default_fill_color,
            **kwargs,
        )
