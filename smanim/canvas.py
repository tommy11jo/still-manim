import base64
from pathlib import Path
from textwrap import dedent
from typing import List, Sequence

import numpy as np

from smanim.config import CONFIG, Config
from smanim.constants import ORIGIN, RADIANS, Z_INDEX_MIN
from smanim.mobject.mobject import Group, Mobject
from smanim.mobject.geometry.polygon import Rectangle
from smanim.mobject.vmobject import VMobject
from smanim.mobject.text.text_mobject import Text
from smanim.typing import InternalPoint3D_Array, Point3D, Vector3
from smanim.utils.color import BLACK
from smanim.utils.logger import log

import itertools as it
import svg

from smanim.utils.space_ops import to_pixel_coords

# make this compatible with pyodide
import sys

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
        cur_mobjects: List[Mobject] = [
            Rectangle(
                width=self.config.fw,
                height=self.config.fh,
                fill_color=BLACK,
                z_index=Z_INDEX_MIN,
            )
        ]
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

    def snapshot(self, preview: bool = False, overwrite: bool = False):
        mobjects_in_order = self.get_mobjects_to_display()
        svg_els_lst: List[svg.Element] = []
        for mobject in mobjects_in_order:
            svg_func = self.get_to_svg_func(mobject)
            if svg_func is None:
                continue
            new_svg_els = svg_func(mobject)
            svg_els_lst.extend(new_svg_els)
        svg_view_obj = svg.SVG(
            viewBox=svg.ViewBoxSpec(0, 0, self.config.pw, self.config.ph),
            elements=svg_els_lst,
        )
        if not overwrite:
            self.num_snapshots += 1
            suffix = self.num_snapshots - 1
        else:
            suffix = 0
        self.save_svg(svg_view_obj, preview=preview, suffix=suffix)

    # Used in pyodide web environment
    # Since the state of python program is maintained across calls to `runPython`, canvas state must be cleared here
    def draw(self):
        self.snapshot(overwrite=True, preview=False)
        self.clear()

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
            height = text_obj.font_height + text_obj.leading
            if i == 0:
                height -= text_obj.leading
                height += text_obj.y_padding_in_pixels

            text_tspan_objs.append(
                svg.TSpan(
                    text=raw_text,
                    x=start_pt[0],
                    dy=height,
                    dx=text_obj.x_padding_in_pixels,
                )
            )
        x_center, y_center = self._to_pixel_coords(text_obj.get_center())[:2]
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

    # Layering
    def move_to_back(self, mobject: Mobject, family: bool = True):
        bottom_z_index = min([mob.z_index for mob in self.mobjects.get_family()])
        mobject.z_index = bottom_z_index - 1
        if family:
            for mobject in self.mobjects.get_family()[1:]:
                mobject.z_index = bottom_z_index - 1

    def move_to_front(self, mobject: Mobject, family: bool = True):
        top_z_index = max([mob.z_index for mob in self.mobjects.get_family()])
        mobject.z_index = top_z_index + 1
        if family:
            for mobject in self.mobjects.get_family()[1:]:
                mobject.z_index = top_z_index + 1

    # Transformations on canvas apply directly to its group
    # Slightly misleading since canvas does not scale itself
    # Gives the impression that canvas is a mobject when it is not
    def scale(self, factor: float, about_point: Point3D | None = ORIGIN) -> None:
        self.mobjects.scale(factor, about_point)

    def shift(self, vector: Vector3) -> None:
        self.mobjects.shift(vector)


canvas = Canvas(CONFIG)
