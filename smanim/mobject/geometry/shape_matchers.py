from typing_extensions import Self

import numpy as np
from smanim.constants import DOWN, LEFT, ORIGIN, OUT, PI, RIGHT, SMALL_BUFF, UP
from smanim.mobject.geometry.line import Line
from smanim.mobject.mobject import Mobject
from smanim.mobject.geometry.polygon import Rectangle
from smanim.mobject.vmobject import VGroup
from smanim.typing import Point3D, Vector3
from smanim.utils.color import RED, YELLOW, ManimColor

__all__ = ["Cross", "SurroundingRectangle"]


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


class SurroundingRectangle(Rectangle):
    """A rectangle surrounding `Mobject`"""

    def __init__(
        self,
        mobject: Mobject,
        stroke_color: ManimColor = YELLOW,
        buff: float = SMALL_BUFF,
        corner_radius: float = 0.0,
        **kwargs,
    ) -> None:
        super().__init__(
            default_stroke_color=stroke_color,
            width=mobject.width + 2 * buff,
            height=mobject.height + 2 * buff,
            corner_radius=corner_radius,
            **kwargs,
        )
        self.buff = buff
        self.surrounded = mobject
        self.move_to(mobject)

    # Transformations just update bounding points
    def rotate(
        self,
        angle: float = PI / 4,
        axis: Vector3 = OUT,
        about_point: Point3D | None = ORIGIN,
    ) -> Self:
        self._update_points()

    def scale(self, factor: float, about_point: Point3D = ORIGIN) -> Self:  # override
        self._update_points()

    def stretch(self, factor: float, dim: int) -> Self:  # override
        self._update_points()

    def shift(self, vector: Vector3) -> Self:  # override
        self._update_points()

    def _update_points(self):
        # calculate the bbox without this surrounding rect interfering
        if self in self.surrounded.submobjects:
            self.surrounded.remove(self)
            bbox = np.array(self.surrounded.get_bbox())
            self.surrounded.add(self)
        else:
            bbox = np.array(self.surrounded.get_bbox())
        self.reset_points_from_vertices(bbox)