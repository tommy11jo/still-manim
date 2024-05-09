from __future__ import annotations
from pathlib import Path
from typing_extensions import Literal, Self
import numpy as np
from smanim.config import CONFIG
from smanim.constants import (
    DEFAULT_FONT_SIZE,
    ORIGIN,
    OUT,
    PI,
    UL,
)
from smanim.mobject.transformable import TransformableMobject
from smanim.typing import Point3D, Vector3
from smanim.utils.color import WHITE, ManimColor
from smanim.utils.space_ops import to_manim_len, to_pixel_len
from smanim.utils.text_ops import wrap_text
from PIL import ImageFont

__all__ = ["Text"]

current_script_directory = Path(__file__).parent

# TODO: move this functionality into config
font_family = "computer-modern"
font_dir = "fonts/computer-modern/"
# (Bold, Italic)
font_paths_by_style = {
    (True, False): "cmunbx.ttf",
    (False, True): "cmunti.ttf",
    (False, False): "cmunrm.ttf",
    (True, True): "cmunbi.ttf",
}
# font_family = "Roboto"
# font_dir = "fonts/Roboto/"
# font_paths_by_style = {
#     (False, False): "Roboto-Regular.ttf",
#     (True, False): "Roboto-Bold.ttf",
#     (False, True): "Roboto-Italic.ttf",
#     (True, True): "Roboto-BoldItalic.ttf",
# }


# FUTURE: Add two text elements together
class Text(TransformableMobject):
    def __init__(
        self,
        text: str,
        position: Point3D = UL,  # coords of upper left corner
        start_angle: float = 0,  # in radians
        color: ManimColor = WHITE,
        opacity: float = 1.0,
        max_width: float | None = 6.0,  # in internal manim units
        z_index: int = 1,  # text is by default above the normal 0 z-index
        font_size: float = DEFAULT_FONT_SIZE,
        text_decoration: Literal[
            "none", "underline", "overline", "line-through"
        ] = "none",
        bold: bool = False,
        italics: bool = False,
        x_padding: float = 0,
        y_padding: float = 0,
        leading: float = 0.2,  # percent (as decimal) of line height for spacing between lines
        **kwargs,
    ):
        if not isinstance(text, str):
            raise ValueError("Text must be a str")
        if len(text) == 0:
            raise ValueError("Text cannot be empty")
        super().__init__(z_index=z_index, **kwargs)
        self.raw_text = text
        self._heading = start_angle

        self.fill_color = color
        self.fill_opacity = opacity
        self.text_decoration = text_decoration
        self.italics = italics
        self.bold = bold
        font_file = font_paths_by_style[(bold, italics)]

        font_path: Path = current_script_directory / font_dir / font_file

        self.setup_text_layout(
            text=text,
            position=position,
            font_family=font_family,
            font_size=font_size,
            font_path=font_path,
            max_width=max_width,
            x_padding=x_padding,
            y_padding=y_padding,
            leading=leading,
        )
        self.move_to_origin()

    # text should not take up more space than it needs, so extra space is ignored
    def setup_text_layout(
        self,
        text: str,
        position: Point3D,
        font_family: str,
        font_size: float,
        font_path: str,
        max_width: float,
        x_padding: float,
        y_padding: float,
        leading: float,
    ):
        # this function also resets the bounding box
        self.font_family = font_family
        self.font_size = font_size
        self.font_path = font_path
        font = ImageFont.truetype(font_path, font_size)
        self.x_padding = x_padding
        self.y_padding = y_padding
        self.x_padding_in_pixels = to_pixel_len(x_padding, CONFIG.pw, CONFIG.fw)
        self.y_padding_in_pixels = to_pixel_len(y_padding, CONFIG.pw, CONFIG.fw)
        max_width_in_pixels = to_pixel_len(max_width, CONFIG.pw, CONFIG.fw)
        self.leading = leading

        # ascent, descent = font.getmetrics()
        # self.font_ascent = ascent
        # Note: Cannot use this since PIL captures maximum ascent possible, which is much more than standard letters
        # Current code allows the bbox to be too small for those non-standard cases

        _, t0, _, b0 = font.getbbox("aGg")
        _, t, _, b = font.getbbox("aG")
        self.font_ascent_pixels = b - t
        self.font_descent_pixels = (b0 - t0) - (b - t)
        leading_pixels = (self.font_ascent_pixels + self.font_descent_pixels) * leading
        self.leading_pixels = leading_pixels

        line_height_in_munits = to_manim_len(
            self.font_ascent_pixels + self.font_descent_pixels, CONFIG.pw, CONFIG.fw
        )
        leading_in_munits = to_manim_len(leading_pixels, CONFIG.pw, CONFIG.fw)

        text_tokens, dims = wrap_text(
            text=text,
            font_path=self.font_path,
            font_size=font_size,
            max_width_in_pixels=max_width_in_pixels,
        )
        self.text_tokens = text_tokens

        self.font_widths = np.array(
            [pair[0] + self.x_padding_in_pixels * 2 for pair in dims]
        )
        # uncertain decision: use max_width or use the max of the actual widths
        line_width_in_munits = (
            max_width
            if len(text_tokens) > 1
            else to_manim_len(self.font_widths[0], CONFIG.pw, CONFIG.fw)
        )

        bbox_height = (
            line_height_in_munits * len(text_tokens)
            + leading_in_munits * (len(text_tokens) - 1)
            + y_padding * 2
        )

        ur = position + np.eye(3)[0] * line_width_in_munits
        ul = position
        dl = ul - np.eye(3)[1] * bbox_height
        dr = ur - np.eye(3)[1] * bbox_height
        self.bounding_points = np.array([ur, ul, dl, dr])

        # Note: this point doesn't change during in-place rotation because SVG applies it after. It still changes for other transformations
        # So, `svg_upper_left` can get out of sync with `bounding_points`. Be careful.
        self.svg_upper_left = ul.copy()

    @property
    def position(self):
        """Returns the upper left corner of this mobject's bounding box"""
        # Warning: See note above, can get out of sync with `svg_upper_left`
        return self.bounding_points[1]

    @property
    def heading(self) -> float:
        return self._heading

    @heading.setter
    def heading(self, value: float) -> None:
        rot = value - self._heading
        self._heading = value
        bounding_points = super().rotate_points(self.bounding_points, rot, OUT, None)
        self.bounding_points = bounding_points

    def __repr__(self):
        class_name = self.__class__.__qualname__
        return f"{class_name}(value={self.raw_text})"

    def rotate_in_place(
        self,
        angle: float = PI / 4,
        axis: Vector3 = OUT,
    ) -> Self:
        return self.rotate(angle, axis, None)

    def rotate(
        self,
        angle: float = PI / 4,
        axis: Vector3 = OUT,
        about_point: Point3D | None = ORIGIN,
    ) -> Self:
        if about_point is None:
            # in-place rotation occurs when `about_point` is None
            # in-place rotation must commute with all other transformations, since it is applied last
            # Leaves the `svg_upper_left` unchanged, since a rotation will be applied to it during svg generation
            self.heading = self.heading + angle  # see `heading` setter
            for mob in self.submobjects:
                mob.rotate(angle, axis, about_point)
            return self
        else:
            # other rotation can freely change upper left and bbox while leaving text intact
            old_center = self.center
            new_center = super().rotate_points(
                np.array([old_center]), angle, axis, about_point
            )[0]
            self.move_to(new_center)
            return self

    # scales both text and bbox, assumes font size is exactly proportional
    # by default, scales using center point as `about_point`
    def scale(self, factor: float, about_point: Point3D | None = None) -> Self:
        bounding_points = super().scale_points(
            self.bounding_points, factor, about_point
        )
        self.bounding_points = bounding_points
        self.svg_upper_left = super().scale_points(
            np.array([self.svg_upper_left]), factor, about_point
        )[0]
        self.font_size *= factor
        self.font_widths *= factor

        self.font_ascent_pixels *= factor
        self.font_descent_pixels *= factor
        self.leading_pixels *= factor
        self.leading *= factor

        for mob in self.submobjects:
            mob.scale(factor, about_point)
        return self

    # Currently stretches both bbox and the text itself
    def stretch(self, factor: float, dim: int) -> Self:
        self.setup_text_layout(
            text=self.raw_text,
            position=self.position,
            font_family=self.font_family,
            font_size=self.font_size,
            font_path=self.font_path,
            max_width=self.width
            * factor,  # keep text appearance the same while stretching the bbox
            x_padding=self.x_padding,
            y_padding=self.y_padding,
            leading=self.leading,
        )

        for mob in self.submobjects:
            mob.stretch(factor, dim)
        return self

    # shifts the text and text bbox
    def shift(self, vector: Vector3) -> Self:
        bounding_points = super().shift_points(self.bounding_points, vector)
        self.bounding_points = bounding_points
        self.svg_upper_left = super().shift_points(
            np.array([self.svg_upper_left]), vector
        )[0]
        for mob in self.submobjects:
            mob.shift(vector)
        return self

    # sets fill color of text itself
    def set_color(self, color: ManimColor, family: bool = False) -> Self:  # override
        self.fill_color = color
        if family:
            for mem in self.get_family()[1:]:
                mem.set_color(color=color, family=True)

    def set_opacity(self, opacity: float, family: bool = False) -> Self:  # override
        self.fill_opacity = opacity
        if family:
            for mem in self.get_family()[1:]:
                mem.set_opacity(opacity=opacity, family=True)

    def __add__(self, text: Text) -> Text:
        chain = self.copy()
        text.next_to(chain, buff=0.0)
        chain.add(text)
        return chain
