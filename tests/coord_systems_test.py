from pathlib import Path
from smanim import *


CONFIG.save_file_dir = Path(__file__).parent / "media"


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
    start_tip = end_tip.copy()
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
    x_axis = NumberLine([-3, 4, 1], include_origin_tick=False)
    y_axis = NumberLine([-4, 1, 1], include_origin_tick=False)
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
    origin_point = axes.coords_to_point(0, 0)
    point_end = axes.coords_to_point(1, 2)
    v = Arrow(origin_point, point_end, fill_color=RED)
    canvas.add(axes, v)
    canvas.snapshot(preview=True)


# graphVector()


def labeledVectorOnGraph():
    axes = Axes()
    canvas.add(axes)
    origin_point = axes.coords_to_point(0, 0)
    point_end = axes.coords_to_point(1, 2)
    y_axis_point = axes.coords_to_point(0, 2)
    x_axis_point = axes.coords_to_point(1, 0)

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


# labeledVectorOnGraph()


def gridLines():
    graph = NumberPlane()
    canvas.add(graph)
    canvas.snapshot(preview=True)


# gridLines()


def simplePlot():
    # x_axis = NumberLine([-2, 2, 1], exclude_origin_tick=True)
    # y_axis = NumberLine([-2, 8, 1], exclude_origin_tick=True)
    # graph = NumberPlane(x_axis=x_axis, y_axis=y_axis)
    graph = NumberPlane.from_axes_ranges(
        (-3, 3), (-2, 9, 2), fill_canvas=True, num_sampled_graph_points_per_tick=15
    )
    # graph.plot(lambda x: x)
    # graph.plot(lambda x: np.sin(x))
    graph.plot(lambda x: x**2)
    # graph.center()
    canvas.add(graph)
    # canvas.scale(2)
    canvas.snapshot(preview=True)


# simplePlot()


# discontinuous test
def discontinuousPlot():
    # x_axis = NumberLine([-3, 3], exclude_origin_tick=True)
    # y_axis = NumberLine([-6, 6], exclude_origin_tick=True)
    # ax1 = NumberPlane(x_axis=x_axis.copy(), y_axis=y_axis.copy()).shift(LEFT)
    # ax2 = NumberPlane(x_axis=x_axis.copy(), y_axis=y_axis.copy()).shift(RIGHT)
    ax1 = NumberPlane.from_axes_ranges((-3, 3), (-6, 6))
    ax2 = NumberPlane.from_axes_ranges((-3, 3), (-6, 6))

    def fn(x):
        return (x**2 - 2) / (x**2 - 4)

    # will error
    # incorrect = ax1.plot(fn, stroke_color=RED)
    correct = ax2.plot(
        fn,
        discontinuities=[-2, 2],  # discontinuous points
        dt=0.1,  # left and right tolerance of discontinuity
        stroke_color=GREEN,
    )
    canvas.add(ax2)
    canvas.snapshot(preview=True)


# discontinuousPlot()
def numberLineSpanning():
    n = NumberLine((-2, 18), length=CONFIG.fh)

    n.rotate(PI / 4)
    # n.rotate(PI / 2)
    canvas.add(Dot(n.coord_to_point(0)))
    canvas.add(Dot(n.start, fill_color=GREEN))
    canvas.add(Dot([0, 0, 0]))
    canvas.add(n)
    canvas.snapshot(preview=True)


# numberLineSpanning()


# TODO: why doesn't this work
# just_sin = NumberPlane().scale(0.3)
# just_sin.plot(np.sin)
# Also fix bug in pyodide regarding reloading of variables
def derivativePlot():
    n = NumberPlane.from_axes_ranges((-6, 6), (-2, 2))
    parabola = n.plot(np.sin, stroke_color=BLUE)
    parabola_deriv_fn = parabola.gen_derivative_fn()
    parabola_deriv = n.plot(parabola_deriv_fn, stroke_color=RED)
    label = Text("y = sin(x)", color=RED, font_size=30).next_to(parabola, UP)
    label.shift(LEFT * 0.6)
    label2 = Text("y = cos(x)", color=BLUE, font_size=30).next_to(parabola_deriv, UP)
    label2.shift(RIGHT * 2)
    canvas.add(n, label, label2)
    canvas.snapshot(preview=True)


derivativePlot()
