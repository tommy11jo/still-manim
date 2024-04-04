import html
from pathlib import Path
from typing_extensions import Literal, Self
import numpy as np
from smanim.constants import (
    OUT,
    PI,
    TEXT_X_PADDING,
    TEXT_Y_PADDING,
    UL,
)
from smanim.mobject.transformable import TransformableMobject
from smanim.typing import Point3D, Vector3
from smanim.config import CONFIG
from smanim.utils.color import WHITE, ManimColor
from smanim.utils.space_ops import to_manim_len, to_pixel_len
from smanim.utils.text_ops import wrap_text
from PIL import ImageFont

__all__ = ["Text"]

current_script_directory = Path(__file__).parent

font_family = "computer-modern"
font_dir = "fonts/computer-modern/"
# (Bold, Italic)
font_paths_by_style = {
    (True, False): "cmunbx.ttf",
    (False, True): "cmunti.ttf",
    (False, False): "cmunrm.ttf",
    (True, True): "cmunbi.ttf",
}


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
        font_size: float = 20,
        text_decoration: Literal[
            "none", "underline", "overline", "line-through"
        ] = "none",
        bold: bool = False,
        italics: bool = False,
        x_padding: float = TEXT_X_PADDING,
        y_padding: float = TEXT_Y_PADDING,
        **kwargs,
    ):
        if not isinstance(text, str):
            raise ValueError("Text must be a str")
        if len(text) == 0:
            raise ValueError("Text cannot be empty")
        super().__init__(z_index=z_index, **kwargs)
        # FUTURE: will need to sanitize if these diagrams can be shared
        text = html.escape(text)
        self.raw_text = text
        self._heading = start_angle

        self.fill_color = color
        self.fill_opacity = opacity
        self.text_decoration = text_decoration
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
        )

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
    ):
        # Note this function also resets the bounding box
        self.font_family = font_family
        self.font_size = font_size
        self.font_path = font_path
        self.x_padding = x_padding
        self.y_padding = y_padding
        self.x_padding_in_pixels = to_pixel_len(x_padding, CONFIG.pw, CONFIG.fw)
        self.y_padding_in_pixels = to_pixel_len(y_padding, CONFIG.pw, CONFIG.fw)
        max_width_in_pixels = to_pixel_len(max_width, CONFIG.pw, CONFIG.fw)
        font = ImageFont.truetype(font_path, font_size)
        # line_height = ascent + descent
        # Workaround: ascent seems to be capturing what ascent + descent typically would
        # I think the bbox is including the descent by default
        ascent, descent = font.getmetrics()
        self.font_ascent = ascent
        self.font_descent = descent
        line_height = ascent
        self.font_height = line_height
        self.leading = line_height * 0.5

        line_height_in_munits = to_manim_len(self.font_height, CONFIG.pw, CONFIG.fw)
        leading_in_munits = to_manim_len(self.leading, CONFIG.pw, CONFIG.fw)
        font_descent_in_munits = to_manim_len(self.font_descent, CONFIG.pw, CONFIG.fw)

        text_tokens, dims = wrap_text(
            text=text,
            font_path=self.font_path,
            font_size=font_size,
            max_width_in_pixels=max_width_in_pixels,
        )

        self.font_widths = np.array(
            [pair[0] + self.x_padding_in_pixels * 2 for pair in dims]
        )
        line_width_in_munits = (
            max_width
            if len(text_tokens) > 1
            else to_manim_len(self.font_widths[0], CONFIG.pw, CONFIG.fw)
        )

        self.text_tokens = text_tokens
        # Note: first line does not having leading space
        bbox_height = (
            line_height_in_munits * len(text_tokens)
            + leading_in_munits * (len(text_tokens) - 1)
            + y_padding * 2
        ) + font_descent_in_munits
        ur = position + np.eye(3)[0] * line_width_in_munits
        ul = position
        dl = ul - np.eye(3)[1] * bbox_height
        dr = ur - np.eye(3)[1] * bbox_height
        self.bounding_points = np.array([ur, ul, dl, dr])

        # Note: this point doesn't change during rotate because SVG applies it after. It still changes for other transformations
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

    def rotate(
        self,
        angle: float = PI / 4,
        axis: Vector3 = OUT,
        about_point: Point3D | None = None,
    ) -> Self:
        # must commute with all other transformations, since it is applied last
        if about_point is not None:
            raise ValueError("Rotation of text mobject must not set `about_point`.")
        # Leaves the `svg_upper_left` unchanged, since a rotation will be applied to it during svg generation
        self.heading = self.heading + angle  # see `heading` setter
        for mob in self.submobjects:
            mob.rotate(angle, axis, about_point)
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
        self.font_height *= factor
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
