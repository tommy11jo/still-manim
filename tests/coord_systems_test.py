from copy import deepcopy
from pathlib import Path
from smanim.canvas import Canvas
from smanim.config import Config
from smanim import *


config = Config(save_file_dir=Path(__file__).parent / "media")
canvas = Canvas(config=config)


# Number line without tip arrows at the start and end
def simpleNumberLine():
    n = NumberLine([-3, 4, 1], include_arrow_tips=False)
    canvas.add(n)
    canvas.snapshot(preview=True)


# simpleNumberLine()


# TODO: fix line cap awkwardness on ends of arrows
# Number line with vector on particular points and with tip arrows at the start and end
def number_line_with_vector():
    n = NumberLine([-3, 4, 1])
    v = Arrow(n.coord_to_point(-2), n.coord_to_point(2), fill_color=RED)
    g = Group(n, v)
    g.scale(1.3)
    canvas.add(g)
    canvas.snapshot(preview=True)


# number_line_with_vector()


# tests using a custom arrow tip as well as styling different groups on the number line
def number_line_custom_arrow_tip():
    # Notice how fill_color gets overridden
    end_tip = Arrow(LEFT / 2, RIGHT / 2, tip_length=0.1, tip_width=0.05, fill_color=RED)
    start_tip = deepcopy(end_tip)
    baby_tips_line = NumberLine(
        [-3, 4, 1],
        start_arrow_tip=start_tip,
        end_arrow_tip=end_tip,
        color=RED,
    )
    baby_tips_line.set_opacity(0.5, family=True)
    baby_tips_line.labels.set_color(color=WHITE)
    baby_tips_line.labels.set_opacity(opacity=1.0)

    canvas.add(baby_tips_line)
    canvas.snapshot(preview=True)


# number_line_custom_arrow_tip()


def axes():
    a = Axes()
    canvas.add(a)
    canvas.snapshot(preview=True)


# axes()


def custom_axes():
    x_axis = NumberLine([-3, 4, 1], exclude_origin_tick=True)
    y_axis = NumberLine([-4, 1, 1], exclude_origin_tick=True)
    a = Axes(x_axis, y_axis)
    a.center()
    canvas.add(a)
    canvas.snapshot(preview=True)


# custom_axes()


def y_axis_shift():
    y_axis = NumberLine()
    y_axis.rotate(PI / 2)
    y_axis.shift(RIGHT)
    canvas.add(y_axis)

    canvas.snapshot(preview=True)


# y_axis_shift()


def graphVector():
    axes = Axes()
    origin_point = axes.point_to_point(0, 0)
    point_end = axes.point_to_point(1, 2)
    v = Arrow(origin_point, point_end, fill_color=RED)
    canvas.add(axes, v)
    canvas.snapshot(preview=True)


# graphVector()


def labeledVectorOnGraph():
    axes = Axes()
    canvas.add(axes)
    origin_point = axes.point_to_point(0, 0)
    point_end = axes.point_to_point(1, 2)
    y_axis_point = axes.point_to_point(0, 2)
    x_axis_point = axes.point_to_point(1, 0)

    comps_group = Group()
    y_comp = Line(x_axis_point, point_end, stroke_color=BLUE)
    y_comp_label = Text("[0, 2]").next_to(y_comp, RIGHT, buff=TINY_BUFF)
    comps_group.add(y_comp, y_comp_label)
    x_comp = Line(y_axis_point, point_end, stroke_color=BLUE)
    x_comp_label = Text("[1, 0]").next_to(x_comp, UP, buff=TINY_BUFF)
    comps_group.add(x_comp, x_comp_label)
    comps_group.set_opacity(0.5)
    canvas.add(comps_group)

    v = Arrow(origin_point, point_end, fill_color=RED)
    v.add_label(Text("v", color=RED))
    canvas.add(v)
    label = Text("Vector Components", font_size=H1_FONT_SIZE)
    label.next_to(axes, UP)
    canvas.add(label)
    canvas.snapshot(preview=True)


labeledVectorOnGraph()
