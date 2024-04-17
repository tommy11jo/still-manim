from smanim.constants import DEFAULT_DOT_RADIUS, ORIGIN, TAU
from smanim.mobject.geometry.arc import Arc
from smanim.mobject.text.text_mobject import Text
from smanim.typing import Point3D
from smanim.utils.color import BLUE, WHITE, ManimColor, has_default_colors_set

__all__ = [
    "Circle",
    "Dot",
    "LabeledDot",
]


class Circle(Arc):
    def __init__(
        self,
        radius: float = 1.0,
        **kwargs,
    ) -> None:
        if not has_default_colors_set(kwargs):
            kwargs["default_fill_color"] = BLUE
        super().__init__(
            radius=radius,
            start_angle=0,
            angle=TAU,
            **kwargs,
        )


class Dot(Circle):
    def __init__(
        self,
        point: Point3D = ORIGIN,
        radius: float = DEFAULT_DOT_RADIUS,
        color: ManimColor | None = None,
        **kwargs,
    ) -> None:
        if not has_default_colors_set(kwargs):
            kwargs["default_fill_color"] = color or WHITE
        super().__init__(
            arc_center=point,
            radius=radius,
            **kwargs,
        )


class LabeledDot(Dot):
    """A `Dot` containing a label at its center"""

    def __init__(
        self,
        label: Text,
        radius: float | None = None,
        **kwargs,
    ):
        if radius is None:
            radius = 0.1 + max(label.width, label.height) / 2
        self.label = label
        super().__init__(radius=radius, **kwargs)
        label.move_to(self.center)
        self.add(label)
