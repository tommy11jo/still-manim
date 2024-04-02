from smanim.constants import DOWN, LEFT, RIGHT, SMALL_BUFF, UP
from smanim.mobject.line import Line
from smanim.mobject.mobject import Mobject
from smanim.mobject.polygon import Rectangle
from smanim.mobject.vmobject import VGroup
from smanim.utils.color import RED, YELLOW, ManimColor

__all__ = ["SurroundingRectangle", "Cross"]


class SurroundingRectangle(Rectangle):
    """A rectangle surrounding `Mobject`"""

    def __init__(
        self,
        mobject: Mobject,
        color: ManimColor = YELLOW,
        buff: float = SMALL_BUFF,
        corner_radius: float = 0.0,
        **kwargs,
    ) -> None:
        super().__init__(
            stroke_color=color,
            width=mobject.width + 2 * buff,
            height=mobject.height + 2 * buff,
            corner_radius=corner_radius,
            **kwargs,
        )
        self.buff = buff
        self.move_to(mobject)


class Cross(VGroup):
    """Used for creating a red cross on top of any mobject"""

    def __init__(
        self,
        mobject: Mobject | None = None,
        stroke_color: ManimColor = RED,
        stroke_opacity: float = 1.0,
        stroke_width: float = 6.0,
        scale_factor: float = 1.0,
        **kwargs,
    ) -> None:
        super().__init__(
            Line(UP + LEFT, DOWN + RIGHT), Line(UP + RIGHT, DOWN + LEFT), **kwargs
        )
        self.stretch_to_fit_width(mobject.width)
        self.stretch_to_fit_height(mobject.height)
        self.move_to(mobject)

        self.scale_in_place(scale_factor)
        self.set_stroke(color=stroke_color, width=stroke_width, opacity=stroke_opacity)
