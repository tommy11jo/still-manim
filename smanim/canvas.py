from __future__ import annotations
import base64
from collections import namedtuple
import html
import inspect
import json
from pathlib import Path
from textwrap import dedent
from typing import List, Tuple

import numpy as np

from smanim.config import CONFIG, Config
from smanim.constants import (
    DOWN,
    LEFT,
    ORIGIN,
    RADIANS,
    RIGHT,
    SMALL_BUFF,
    UL,
    UP,
    Z_INDEX_MIN,
)
from smanim.mobject.geometry.polygon import Rectangle
from smanim.mobject.group import Group
from smanim.mobject.mobject import AccessPath, AccessType, Mobject
from smanim.mobject.vmobject import VGroup, VMobject
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


MobjectMetadata = namedtuple(
    "MobjectMetadata",
    ["id", "type", "points", "children", "parent", "classname", "path", "lineno"],
)


# for now, instance must be named lowercase 'canvas' to work with access paths for bidirectional features
class Canvas:
    def __init__(self, config: Config):
        self.reset_canvas(config)

    def reset_canvas(self, config: Config):
        self.config = config

        self.mobjects = Group()
        self.num_snapshots = 0
        self.loaded_fonts = set()

    def add(self, *mobjects: Mobject):
        for mobject in mobjects:
            if not isinstance(mobject, Mobject):
                raise ValueError(f"Added item must be of type Mobject: {mobject}")
            if mobject in self.mobjects:
                log.warning(f"Mobject already added: {mobject}")
            else:
                # assume this fn is called from the main file
                caller_frame = inspect.stack()[1]
                lineno = caller_frame.lineno
                old_len = len(self.mobjects)
                # TODO: Remove would break the index set within subpath here.
                # A major fix would be to make canvas a `mobject`. This has other benefits too.
                # Then I could use mob_id and parent for index lookup (base mobject functionality)
                # For now, I'm removing remove so that this doesn't break things
                new_access_path = AccessPath(
                    type=AccessType.ADD_TO_CANVAS,
                    subpath=f"canvas.mobjects[{old_len}]",
                    parent=None,
                    lineno=lineno,
                )
                mobject.access_paths.append(new_access_path)

                self.mobjects.add(mobject)

    # def remove(self, *mobjects: Mobject):
    #     for mobject in mobjects:
    #         if mobject not in self.mobjects:
    #             log.warning(f"Mobject not found: {mobject}")
    #         else:
    #             self.mobjects.remove(mobject)

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
            VGroup: self.group_to_svg_el,
            Group: self.group_to_svg_el,
            VMobject: self.vmobject_to_svg_el,  # includes VGroup handling
            Text: self.text_to_svg_el,
            Mobject: self.group_to_svg_el,
        }
        for _type in to_svg_funcs:
            if isinstance(mobject, _type):
                return to_svg_funcs[_type]
        raise TypeError(f"Displaying an object of class {_type} is not supported")

    def snapshot(
        self,
        preview: bool = True,
        overwrite: bool = False,
        ignore_bg: bool = False,
        crop: bool = False,
        crop_buff: float = SMALL_BUFF,
        called_from_draw: bool = False,
        manual_suffix: str | None = None,
    ) -> Tuple[Tuple[float, float, float, float], dict]:
        if not called_from_draw and BROWSER_ENV:
            raise Exception(
                "Please use `canvas.draw()` instead of `canvas.snapshot` in the browser env."
            )

        bg_rect = None
        if self.config.bg_color is not None and not ignore_bg:
            bg_rect = Rectangle(
                width=self.config.fw,
                height=self.config.fh,
                fill_color=self.config.bg_color,
                z_index=Z_INDEX_MIN,
                parent=None,
                subpath="canvas.mobjects[0]",
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
            if new_svg_els is not None:
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
            id="smanim-canvas",
            viewBox=svg.ViewBoxSpec(x, y, w, h),
            elements=svg_els_lst,
        )
        if not overwrite:
            self.num_snapshots += 1
            suffix = self.num_snapshots - 1
        else:
            suffix = 0
        if manual_suffix is not None:
            suffix = manual_suffix
        self.save_svg(svg_view_obj, preview=preview, suffix=suffix)

        layer_metadatas = {}
        # include the top canvas layer

        layer_metadatas["canvas"] = self._create_mobject_metadata(
            mobject=None,
            id="canvas",
            mob_type="canvas",
            parent="None",
            children=[f"id-{id(mob)}" for mob in self.mobjects],
        )

        for mobject in self.mobjects:
            self.populate_mobject_metadatas(mobject, layer_metadatas)
        if bg_rect is not None:
            self.populate_mobject_metadatas(bg_rect, layer_metadatas, is_bg_rect=True)

        return (x, y, w, h), layer_metadatas

    # Used in pyodide web environment
    # Since the state of python program is maintained across calls to `runPython`, canvas state must be cleared here
    def draw(
        self, crop: bool = False, ignore_bg: bool = False, crop_buff: float = SMALL_BUFF
    ) -> str:
        bbox, metadata = self.snapshot(
            overwrite=True,
            preview=False,
            crop=crop,
            ignore_bg=ignore_bg,
            crop_buff=crop_buff,
            called_from_draw=True,
        )
        self.reset_canvas(self.config)
        return json.dumps({"bbox": bbox, "metadata": metadata})

    def vmobject_to_svg_el(
        self, vmobject: VMobject, decimal_precision: int = 3
    ) -> Tuple[svg.Element] | None:
        if len(vmobject.points) == 0:  # handles VGroups
            return None
        points = self._to_pixel_coords(
            vmobject.points, decimal_precision=decimal_precision
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

        if vmobject.stroke_opacity and vmobject.stroke_width:
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

        return (svg.Path(id=f"id-{id(vmobject)}", d=svg_path, **kwargs),)

    def text_to_svg_el(self, text_obj: Text) -> Tuple[svg.Element] | None:

        start_pt = self._to_pixel_coords(text_obj.svg_upper_left)

        font_family = text_obj.font_family
        italics = text_obj.italics
        bold = text_obj.bold
        font_size = text_obj.font_size

        with open(text_obj.font_path, "rb") as font_file:
            font_data = font_file.read()
        base64_font = base64.b64encode(font_data).decode("utf-8")

        # can use foreign object to handle max_width and text wrapping in browser envs, but not for local svg
        obj_id = f"id-{id(text_obj)}"

        family_name_with_style = font_family
        family_name_with_style += "italics" if italics else ""
        family_name_with_style += "bold" if bold else ""
        font_style_inline_font = dedent(
            f"""
            .styleClass-{obj_id} {{
                text-decoration: {text_obj.text_decoration};
                fill: {text_obj.fill_color.value};
                font-size: {font_size}px;
                fill-opacity: {text_obj.fill_opacity};
                font-family: {family_name_with_style};
            }}
            """
        )
        if (font_family, italics, bold) not in self.loaded_fonts:
            font_style_inline_font += f"@font-face {{ font-family: {family_name_with_style}; src: url(data:font/otf;base64,{base64_font}) format('opentype'); }}"
            self.loaded_fonts.add((font_family, italics, bold))

        text_tspan_objs = []

        for i, raw_text in enumerate(text_obj.text_tokens):
            # FUTURE: will need to sanitize if these diagrams can be shared
            text = html.escape(raw_text)
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
                    text=text,
                    x=start_pt[0],
                    dy=height,
                    dx=text_obj.x_padding_in_pixels,
                )
            )
        x_center, y_center = self._to_pixel_coords(text_obj.center)[:2]
        text_svg_obj = svg.Text(
            id=obj_id,
            elements=text_tspan_objs,
            x=start_pt[0],
            y=start_pt[1],
            class_=[f"styleClass-{obj_id}"],
            # svg transform is clockwise, so negate it
            transform=[
                svg.Rotate(a=-text_obj.heading * RADIANS, x=x_center, y=y_center)
            ],
        )

        return (svg.Style(text=font_style_inline_font), text_svg_obj)

    # handles complex mobjects with submobjects as well as groups
    def group_to_svg_el(self, mobject: Mobject, decimal_precision: int = 3):
        bbox_in_pixels = self._to_pixel_coords(
            np.array(mobject.bbox), decimal_precision=decimal_precision
        )
        ul = bbox_in_pixels[1].tolist()
        width = self._to_pixel_len(mobject.width)
        height = self._to_pixel_len(mobject.height)

        rect = svg.Rect(
            id=f"id-{id(mobject)}",
            fill="transparent",
            # fill="rgba(0, 100, 100, 0.4)",
            x=ul[0],
            y=ul[1],
            width=width,
            height=height,
        )
        return (rect,)

    def _to_pixel_coords(
        self,
        points: Point3D | InternalPoint3D_Array,
        decimal_precision: int | None = None,
    ) -> InternalPoint3D_Array:
        if points.shape == (3,):
            point = points
            return to_pixel_coords(
                np.array([point]),
                self.config.pw,
                self.config.ph,
                self.config.fw,
                self.config.fh,
                self.config.fc,
                decimal_precision=decimal_precision,
            )[0]
        else:
            return to_pixel_coords(
                points,
                self.config.pw,
                self.config.ph,
                self.config.fw,
                self.config.fh,
                self.config.fc,
                decimal_precision=decimal_precision,
            )

    def _to_pixel_len(self, value, decimal_precision: int = 3):
        return to_pixel_len(
            value,
            self.config.pw,
            self.config.fw,
            decimal_precision=decimal_precision,
        )

    def _get_mobject_data_attrs(
        self, mobject: Mobject, decimal_precision: int = 3
    ) -> dict:
        return self._create_mobject_metadata(
            mobject=mobject,
            mob_type="mobject",
            id=f"id-{id(mobject)}",
        )

    def _get_group_data_attrs(self, group: Group, decimal_precision: int = 3) -> dict:
        return self._create_mobject_metadata(
            mobject=group,
            mob_type="group",
            id=f"id-{id(group)}",
        )

    def _get_vmobject_data_attrs(
        self, vmobject: VMobject, decimal_precision: int = 3
    ) -> dict:
        """Get the data attributes of this vmobject for the bidirectional editor"""
        points_in_pixels = self._to_pixel_coords(
            vmobject.points, decimal_precision=decimal_precision
        ).tolist()

        return self._create_mobject_metadata(
            id=f"id-{id(vmobject)}",
            mob_type="vmobject",
            mobject=vmobject,
            points=points_in_pixels,
        )

    def _get_text_obj_data_attrs(
        self, text_obj: Text, decimal_precision: int = 3
    ) -> dict:
        """Get the data attributes of this text object for the bidirectional editor."""
        return self._create_mobject_metadata(
            mobject=text_obj,
            mob_type="text",
            id=f"id-{id(text_obj)}",
        )

    def _create_mobject_metadata(
        self,
        mobject: Mobject | None,
        id: str | None = None,
        mob_type: str | None = None,
        children: List[str] | None = None,
        parent: str | None = None,
        points: List[float] | None = None,
    ) -> dict:
        path, lineno = mobject.get_access_path() if mobject else ("", -1)
        path = "None" if path is None else path
        lineno = -1 if lineno is None else lineno
        return MobjectMetadata(
            id=id,
            type=mob_type,
            points=points,
            children=children,
            parent=parent,
            classname=type(mobject).__qualname__ if mobject else "None",
            path=path,
            lineno=lineno,
        )._asdict()

    def populate_mobject_metadatas(
        self, mobject: Mobject, metadatas: dict, parent=None, is_bg_rect=False
    ) -> None:
        mob_id = f"id-{id(mobject)}"
        if is_bg_rect:
            mob_id = "bg_rect"
            # bg_rect is an exception to the rule that metadatas is a map from id => metadata
            # and that the id correspond to the svg element id
            # bg_rect => metadata which has the true id of the bg_rect element
        if parent is None:
            parent_id = "canvas"
        else:
            parent_id = f"id-{id(parent)}"
            metadatas[parent_id]["children"].append(mob_id)
        if isinstance(mobject, VGroup):
            bi_kwargs = self._get_group_data_attrs(mobject)
        elif isinstance(mobject, Group):
            bi_kwargs = self._get_group_data_attrs(mobject)
        elif isinstance(mobject, VMobject):
            bi_kwargs = self._get_vmobject_data_attrs(mobject)
        elif isinstance(mobject, Text):
            bi_kwargs = self._get_text_obj_data_attrs(mobject)
        elif isinstance(mobject, Mobject):
            bi_kwargs = self._get_mobject_data_attrs(mobject)
        else:
            raise Exception(f"Mobject of type {type(mobject)} not handled")
        bi_kwargs["parent"] = parent_id
        bi_kwargs["children"] = []
        metadatas[mob_id] = bi_kwargs
        for child in mobject.submobjects:
            self.populate_mobject_metadatas(child, metadatas, mobject)

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

    @property
    def left(self):
        return self.config.fw / 2 * LEFT

    @property
    def right(self):
        return self.config.fw / 2 * RIGHT

    @property
    def top(self):
        return self.config.fh / 2 * UP

    @property
    def bottom(self):
        return self.config.fh / 2 * DOWN

    @property
    def width(self):
        return self.right[0] - self.left[0]

    @property
    def height(self):
        return self.top[1] - self.bottom[1]

    ## `canvas` operations that change the underlying config
    def set_background(self, color: ManimColor) -> Canvas:
        self.config.bg_color = color
        return self

    def set_dimensions(self, width: int, height: int) -> Canvas:
        # Values here are in manim units
        self.config.fw = width
        self.config.pw = int(width * self.config.density)

        self.config.fh = height
        self.config.ph = int(height * self.config.density)
        return self

    def set_global_text_styles(
        self,
        color: ManimColor | None = None,
        font_size: int | None = None,
        font_family: str | None = None,
    ) -> Canvas:
        """Sets the global text styles, which apply to all text created after this function call"""
        if color is not None:
            self.config.default_text_color = color
        if font_size is not None:
            self.config.default_text_font_size = font_size
        if font_family is not None:
            self.config.default_text_font_family = font_family
        return self

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
