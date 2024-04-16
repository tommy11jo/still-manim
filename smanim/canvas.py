from __future__ import annotations
import base64
import json
from pathlib import Path
from textwrap import dedent
from typing import List, Sequence, Tuple

import numpy as np

from smanim.config import CONFIG, Config
from smanim.constants import (
    ORIGIN,
    RADIANS,
    SMALL_BUFF,
    UL,
    Z_INDEX_MIN,
)
from smanim.mobject.geometry.polygon import Rectangle
from smanim.mobject.group import Group
from smanim.mobject.mobject import Mobject
from smanim.mobject.vmobject import VMobject
from smanim.mobject.text.text_mobject import Text
from smanim.typing import InternalPoint3D_Array, Point3D, Vector3
from smanim.utils.color import ManimColor
from smanim.utils.logger import log

import itertools as it
import svg

from smanim.utils.space_ops import to_pixel_coords, to_pixel_len

import sys

# only use subprocess locally, not in browser with pyodide
BROWSER_ENV = True
if "pyodide" not in sys.modules:
    import subprocess

    BROWSER_ENV = False


__all__ = ["canvas", "Canvas"]


class Canvas:
    def __init__(self, config: Config):
        self.config = config

        self.mobjects = Group()
        self.num_snapshots = 0
        self.loaded_fonts = set()

    def add(self, *mobjects):
        for mobject in mobjects:
            if not isinstance(mobject, Mobject):
                raise ValueError("Added item must be of type Mobject")
            if mobject in self.mobjects:
                log.warning(f"Mobject already added: {mobject}")
            else:
                self.mobjects.add(mobject)

    def remove(self, *mobjects):
        for mobject in mobjects:
            if mobject not in self.mobjects:
                log.warning(f"Mobject not found: {mobject}")
            else:
                self.mobjects.remove(mobject)

    def clear(self):
        self.mobjects = Group()

    def get_mobjects_to_display(
        self,
        use_z_index=True,
    ):
        cur_mobjects: List[Mobject] = []
        cur_mobjects += it.chain(*(m.get_family() for m in self.mobjects))

        if use_z_index:
            return sorted(cur_mobjects, key=lambda m: m.z_index)
        return cur_mobjects

    def get_to_svg_func(self, mobject: Mobject):
        to_svg_funcs = {
            VMobject: self.vmobject_to_svg_el,  # includes VGroup handling
            Text: self.text_to_svg_el,
            Mobject: None,
        }
        for _type in to_svg_funcs:
            if isinstance(mobject, _type):
                return to_svg_funcs[_type]
        raise TypeError(f"Displaying an object of class {_type} is not supported")

    def snapshot(
        self,
        preview: bool = False,
        overwrite: bool = False,
        ignore_bg: bool = False,
        crop: bool = False,
        crop_buff: float = SMALL_BUFF,
        called_from_draw: bool = False,
    ) -> Tuple[float, float, float, float]:
        if not called_from_draw and BROWSER_ENV:
            raise Exception(
                "Please use `canvas.draw()` instead of `canvas.snapshot` in the browser env."
            )
        if self.config.bg_color is not None and not ignore_bg:
            bg_rect = Rectangle(
                width=self.config.fw,
                height=self.config.fh,
                fill_color=self.config.bg_color,
                z_index=Z_INDEX_MIN,
            )
            mobjects_in_order = [bg_rect] + self.get_mobjects_to_display()
        else:
            mobjects_in_order = self.get_mobjects_to_display()
        svg_els_lst: List[svg.Element] = []
        for mobject in mobjects_in_order:
            svg_func = self.get_to_svg_func(mobject)
            if svg_func is None:
                continue
            new_svg_els = svg_func(mobject)
            svg_els_lst.extend(new_svg_els)
        if crop:
            x_munits, y_munits = self.mobjects.get_corner(UL)[:2]
            buffed_upper_left = np.array(
                [x_munits - crop_buff, y_munits + crop_buff, 0]
            )
            x, y = to_pixel_coords(
                [buffed_upper_left],
                config=self.config,
            )[0]

            w_munits, h_munits = self.mobjects.width, self.mobjects.height
            w_munits += 2 * crop_buff
            h_munits += 2 * crop_buff
            w = to_pixel_len(w_munits, self.config.pw, self.config.fw)
            h = to_pixel_len(h_munits, self.config.pw, self.config.fw)
        else:
            x, y, w, h = 0, 0, self.config.pw, self.config.ph
        svg_view_obj = svg.SVG(
            viewBox=svg.ViewBoxSpec(x, y, w, h),
            elements=svg_els_lst,
        )
        if not overwrite:
            self.num_snapshots += 1
            suffix = self.num_snapshots - 1
        else:
            suffix = 0
        self.save_svg(svg_view_obj, preview=preview, suffix=suffix)
        return x, y, w, h

    # Used in pyodide web environment
    # Since the state of python program is maintained across calls to `runPython`, canvas state must be cleared here
    def draw(
        self, crop: bool = False, crop_buff: float = SMALL_BUFF
    ) -> Tuple[float, float, float, float]:
        bbox = self.snapshot(
            overwrite=True,
            preview=False,
            crop=crop,
            crop_buff=crop_buff,
            called_from_draw=True,
        )
        self.clear()
        return json.dumps(bbox)

    def vmobject_to_svg_el(self, vmobject: VMobject) -> Sequence[svg.Element]:
        if len(vmobject.points) == 0:  # handles VGroups
            return []
        points = to_pixel_coords(
            vmobject.points,
            self.config.pw,
            self.config.ph,
            self.config.fw,
            self.config.fh,
            self.config.fc,
        )
        if len(points) == 0:
            return

        quads = vmobject.get_points_in_quads(points)
        svg_path = []
        start = quads[0][0]
        # assumes a continuous path, no subpaths (for now)
        svg_path.append(svg.M(*start[:2]))
        for _p0, p1, p2, p3 in quads:
            svg_path.append(svg.C(*p1[:2], *p2[:2], *p3[:2]))

        if vmobject.is_closed:
            svg_path.append(svg.Z())
        kwargs = {}

        def orNone(value: any):
            return value if value is not None else "none"

        if vmobject.stroke_opacity > 0.0 and vmobject.stroke_width > 0.0:
            kwargs["stroke"] = orNone(
                None
                if not vmobject.stroke_color
                else orNone(vmobject.stroke_color.value)
            )
            kwargs["stroke_width"] = orNone(vmobject.stroke_width)
            # Note: stroke_opacity as an svg arg set to "none" creates an opaque effect
            kwargs["stroke_opacity"] = orNone(vmobject.stroke_opacity)
        kwargs["fill_opacity"] = orNone(vmobject.fill_opacity)
        kwargs["fill"] = orNone(
            None if not vmobject.fill_color else orNone(vmobject.fill_color.value)
        )
        kwargs["stroke_dasharray"] = vmobject.stroke_dasharray

        return (svg.Path(d=svg_path, **kwargs),)

    def _to_pixel_coords(self, points: Point3D | InternalPoint3D_Array):
        if points.shape == (3,):
            point = points
            return to_pixel_coords(
                np.array([point]),
                self.config.pw,
                self.config.ph,
                self.config.fw,
                self.config.fh,
                self.config.fc,
            )[0]
        else:
            return to_pixel_coords(
                points,
                self.config.pw,
                self.config.ph,
                self.config.fw,
                self.config.fh,
                self.config.fc,
            )

    def text_to_svg_el(self, text_obj: Text):

        start_pt = self._to_pixel_coords(text_obj.svg_upper_left)

        font_family = text_obj.font_family
        font_size = text_obj.font_size

        with open(text_obj.font_path, "rb") as font_file:
            font_data = font_file.read()
        base64_font = base64.b64encode(font_data).decode("utf-8")

        # can use foreign object to handle max_width and text wrapping in browser envs, but not for local svg
        id = int(np.random.rand() * 10_000_000)

        font_style_inline_font = dedent(
            f"""
            .styleClass{id} {{
                text-decoration: {font_family};
                fill: {text_obj.fill_color.value};
                font-size: {font_size}px;
                fill-opacity: {text_obj.fill_opacity};
                font-family: {font_family};
            }}
            """
        )
        if font_family not in self.loaded_fonts:
            font_style_inline_font += f"@font-face {{ font-family: {font_family}; src: url(data:font/otf;base64,{base64_font}) format('opentype'); }}"
            self.loaded_fonts.add(font_family)

        text_tspan_objs = []

        for i, raw_text in enumerate(text_obj.text_tokens):
            height = (
                text_obj.font_ascent_pixels
                + text_obj.font_descent_pixels
                + text_obj.leading_pixels
            )
            if i == 0:
                height -= text_obj.leading_pixels
                # don't count the previous line font descent since this draws on the baseline
                height -= text_obj.font_descent_pixels
                height += text_obj.y_padding_in_pixels

            text_tspan_objs.append(
                svg.TSpan(
                    text=raw_text,
                    x=start_pt[0],
                    dy=height,
                    dx=text_obj.x_padding_in_pixels,
                )
            )
        x_center, y_center = self._to_pixel_coords(text_obj.center)[:2]
        text_svg_obj = svg.Text(
            elements=text_tspan_objs,
            x=start_pt[0],
            y=start_pt[1],
            class_=[f"styleClass{id}"],
            # svg transform is clockwise, so negate it
            transform=[
                svg.Rotate(a=-text_obj.heading * RADIANS, x=x_center, y=y_center)
            ],
        )

        return svg.Style(text=font_style_inline_font), text_svg_obj

    def save_svg(
        self,
        svg_obj: svg.SVG,
        name: str = "test",
        preview: bool = False,
        suffix: int | str = "",
    ):
        self.config.mk_save_dir_if_not_exists()
        script_dir = Path(self.config.save_file_dir)
        fpath = script_dir / f"{name}{suffix}.svg"

        with open(fpath, "w") as file:
            file.write(str(svg_obj))
        if preview:
            if BROWSER_ENV:
                raise Exception("Cannot open a preview while running in a browser env")
            subprocess.run(["open", fpath])

    # Transformations on canvas apply directly to its group
    # Slightly misleading since canvas does not scale itself
    # Gives the impression that canvas is a mobject when it is not
    def scale(self, factor: float, about_point: Point3D | None = ORIGIN) -> None:
        self.mobjects.scale(factor, about_point)

    def shift(self, vector: Vector3) -> None:
        self.mobjects.shift(vector)

    # Common helper functions that really change the underlying config
    def set_background(self, color: ManimColor) -> Canvas:
        self.config.bg_color = color
        return self

    # Values here are in manim units
    def set_dimensions(self, width: int, height: int) -> None:
        self.config.fw = width
        self.config.pw = int(width * self.config.density)

        self.config.fh = height
        self.config.ph = int(height * self.config.density)

    def scale_to_fit(self, buff: float = SMALL_BUFF):
        """Scales all mobjects so that they fit on this canvas
        Typically run just before draw() or snapshot()"""
        w, h = self.mobjects.width, self.mobjects.height
        goal_w, goal_h = self.config.fw - 2 * buff, self.config.fh - 2 * buff
        w_scalar = min(1, goal_w / w)
        h_scalar = min(1, goal_h / h)
        scalar = min(w_scalar, h_scalar)
        if scalar != 1:
            self.mobjects.scale(scalar)
        return self


canvas = Canvas(CONFIG)
