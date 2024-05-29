import json
from pathlib import Path
from smanim import *
from smanim.utils.space_ops import mirror_vector

# config = Config(save_file_dir=Path(__file__).parent / "media")
CONFIG.save_file_dir = Path(__file__).parent / "media"
canvas = Canvas(CONFIG)


def simple_square():
    s = Square()
    canvas.add(s)
    canvas.snapshot()


# simple_square()


def simple_triangle():
    t = Triangle()
    canvas.add(t)
    canvas.snapshot()


# simple_triangle()


def square_stroke():
    # this shows that SVG draws stroke equally on inner and outer border
    s1 = Square(stroke_color=BLUE, stroke_width=30).shift(LEFT * 2)
    canvas.add(s1)
    canvas.snapshot()


# square_stroke()


def polygons_next_to():
    s = Square(side_length=0.5)
    canvas.add(s)

    r = Rectangle(1, 2)
    s.next_to(r, DOWN).align_to(r, RIGHT)
    canvas.add(r)

    t = Triangle()
    t.next_to(s, RIGHT).align_to(t, DOWN)
    canvas.add(t)

    canvas.snapshot()
    # canvas.add(s)
    # canvas.snapshot()

    # c = Circle()
    # canvas.add(c)
    # c.next_to(s)
    # c.shift(RIGHT)

    # a = Arrow(s, c)
    # t = Text("hi")
    # canvas.add(a)


# polygons_next_to()


def align_square():
    s = Square(side_length=0.5)
    s1 = Square().scale(2)
    s.align_to(s1, edge=UP)
    canvas.add(s)
    canvas.add(s1)
    canvas.snapshot()


# align_square()


def rotate_hexagon():
    p = RegularPolygon()
    p.rotate(PI / 30)
    canvas.add(p)
    canvas.snapshot()


# rotate_hexagon()


def position_square():
    s = Square()
    s.set_position([4, 2])
    # s.set_x(4)
    # s.set_y(3)
    canvas.add(s)

    canvas.snapshot()


# position_square()


def stroke_and_fill():
    s1 = Square(fill_color=RED)
    s1.set_stroke(ORANGE)
    # now, both fill and stroke will show

    s2 = Square(fill_color=BLUE).shift(RIGHT * 2.1)
    s2.set_fill(color=GREEN)
    # this time, the fill color overrides
    canvas.add(s2)
    canvas.add(s1)
    canvas.snapshot()


# stroke_and_fill()


def stroke_family():
    s1 = Square(fill_color=RED)
    s2 = Square().shift(LEFT * 2.1)
    s3 = Square().shift(DOWN * 2.1)
    s4 = Rectangle().shift(UP * 2.1)
    s2.add(s4)
    s1.add(s2, s3)
    s1.set_stroke(ORANGE, family=True)
    # s1.set_stroke(ORANGE, family=False)
    canvas.add(s1)
    canvas.snapshot()


# stroke_family()


def group_with_submobject():
    s1 = Square()
    s2 = Square().shift(LEFT * 2.1)
    s3 = Square().shift(RIGHT * 2.1)
    s4 = Square(fill_color=YELLOW).shift(UP * 2.1)
    canvas.add(s4)

    s3.set_fill(RED)
    s2.add(s3)
    v = VGroup(s1, s2)
    # v.set_fill(GREEN)
    v.set_stroke(BLUE)
    canvas.add(v)
    canvas.snapshot()


# group_with_submobject()


def polygon_z_index():
    s1 = Square(stroke_color=YELLOW).scale(0.5)
    s2 = Square().shift(LEFT).scale(0.5)
    g1 = VGroup(s1, s2).shift(UP)
    t2 = Text("z-index for both squares default to 0").next_to(g1, UP)
    canvas.add(g1, t2)
    s3 = Square(stroke_color=YELLOW).scale(0.5)
    s4 = Square(z_index=-1).shift(LEFT).scale(0.5)
    g2 = VGroup(s3, s4).shift(DOWN)
    t2 = Text("z-index for red square set to -1").next_to(g2, UP)
    canvas.add(g2, t2)
    # s2 = Square(z_index=-1).shift(LEFT)
    canvas.snapshot()


# polygon_z_index()


def polygon_bring_to_back():
    s1 = Square(stroke_color=YELLOW).scale(0.5)
    s2 = Square().shift(LEFT).scale(0.5)
    g1 = VGroup(s1, s2).shift(UP)
    t2 = Text("z-index for both squares default to 0").next_to(g1, UP)
    canvas.add(g1, t2)
    s3 = Square(stroke_color=YELLOW).scale(0.5)
    s4 = Square().shift(LEFT).scale(0.5)
    g2 = VGroup(s3, s4).shift(DOWN)
    g2.bring_to_back(s4)
    t2 = Text("Red square brought to back within group g2").next_to(g2, UP)
    canvas.add(g2, t2)
    # s2 = Square(z_index=-1).shift(LEFT)
    canvas.snapshot()


# polygon_bring_to_back()


def square_to_rect_line():
    s = Square().shift(UL)
    r = Rectangle().shift(DR * 2)
    line = Line(s, r, dashed=True)
    canvas.add(s)
    canvas.add(r)
    canvas.add(line)
    canvas.snapshot()


# square_to_rect_line()


def square_to_square_arrow():
    left = Square().shift(LEFT * 2)
    right = Square().shift(RIGHT * 2)
    arrow = Arrow(left, right)
    canvas.add(arrow, left, right)
    canvas.snapshot()


# square_to_square_arrow()


def dashed_arrow():
    s = Square().shift(UL)
    r = Rectangle().shift(DR * 2)
    arrow = Arrow(s, r, buff=0.2, dashed=True)
    canvas.add(s, r, arrow)

    canvas.snapshot()


# dashed_arrow()


def simple_arcs():
    quarter_circle = Arc().shift(LEFT * 3)
    canvas.add(quarter_circle)
    circle = Circle(fill_color=BLUE)
    circle.next_to(quarter_circle)
    canvas.add(circle)

    half_circle = Arc.from_points(UR, DR, radius=1)
    half_circle.next_to(quarter_circle, LEFT)
    canvas.add(half_circle)
    canvas.snapshot()


# simple_arcs()


def arc_to_arc_arrow():
    arc = Arc()
    canvas.add(arc)

    arc2 = Arc.from_points(UR, DR, radius=1)
    arc2.shift(UL * 2)
    # example of janky bounding polygon debugging
    canvas.add(arc2)
    a = Arrow(arc, arc2)
    canvas.add(a)

    # shows the bounding box that helps determine arrows end point
    for pt in arc2.bounding_points:
        d = Dot(np.array(pt), fill_color=BLUE)
        canvas.add(d)

    canvas.snapshot()


# arc_to_arc_arrow()


def simple_brace():
    s = Square()
    b = Brace.from_mobject_edge(s)
    canvas.add(s, b)
    canvas.snapshot()


# simple_brace()


def brace_on_text_and_shapes():
    c = Circle()
    b = Brace.from_mobject_edge(c)
    g = VGroup(c, b).shift(LEFT * 3)
    canvas.add(g)

    l1 = Line()
    b1 = Brace.from_mobject_edge(l1)
    g1 = VGroup(l1, b1).shift(UP * 2)
    canvas.add(g1)
    t = Text("brace for it")
    # Demo of how brace location is determined from bounding points
    for d in t.bounding_points:
        canvas.add(Dot(d))
    b2 = Brace.from_mobject_edge(t, buff=0.0)
    g2 = Group(t, b2)
    canvas.add(g2)
    canvas.snapshot()


# brace_on_text_and_shapes()


def labeled_brace():
    r = Rectangle().shift(DOWN)
    l2 = LabeledBrace(
        start=r.get_corner(DL),
        end=r.get_corner(UR),
        label=Text("First", font_size=10),
        label_buff=0,
    )
    r2 = Rectangle().rotate(PI / 6).shift(UP * 1.5)
    text = Text("second", font_size=10)
    l3 = LabeledBrace(r2.vertices[0], r2.vertices[2], label=text, label_buff=0)
    canvas.add(r2, l3)

    canvas.add(r, l2)
    canvas.snapshot()


# labeled_brace()


def brace_span():
    c = Circle()
    b = Brace.from_mobject_edge(c, UP)
    b2 = Brace.from_mobject_edge(c, DOWN, color=RED)
    b3 = Brace.from_mobject_edge(c, RIGHT, color=BLUE)
    canvas.add(c, b, b2, b3)

    s = Square().shift(UR * 3)
    b1 = LabeledBrace.from_mobject_edge(s, LEFT, label=Text("left"))
    canvas.add(s, b1)
    canvas.snapshot()


# brace_span()


def wrapping_text():
    s = Square().shift(DOWN * 2.5)
    canvas.add(s)
    t = Text(
        "hi there the terminal is beautiful and DARK like the night SKY and now let's see if the heights are correct during text wrap and no i don't think it is working and it's not just the lines with CAPS that are the problem. Ok corrected.",
        max_width=2.0,
    )
    # t = Text("thistextispastthewidthbutstaysasone", max_width=2.0)
    # t = Text("and thistextispastthewidthbutstaysasone", max_width=2.0)
    # t.next_to(s)
    canvas.add(t)
    canvas.snapshot()


# wrapping_text()


def text_with_html_chars():
    t = Text("&&hi&&")
    canvas.add(t)
    canvas.snapshot()


# text_with_html_chars()


def arrow_scale():
    # a = Arrow(LEFT, RIGHT)
    a = Arrow(DL, UR)
    # a.scale(2)
    a.scale(0.5)
    canvas.add(a)
    canvas.snapshot()


# arrow_scale()


def submobject_scale():
    s = Square().shift(UR * 3)
    s.add(Square().shift(UR))
    s.scale(0.6)
    canvas.add(s)
    canvas.snapshot()


# submobject_scale()


def scale_group():
    g = VGroup()
    t = Text("hi there").shift(UR * 2).rotate(-PI / 2).scale(2)
    s = Square().shift(DL)
    g.add(s)
    g.add(t)
    # a = Arrow(t, s)
    line = Line(t, s)
    g.add(line)
    # g.add(a)
    # g.scale(0.2)

    canvas.add(g)
    canvas.snapshot()


# scale_group()


def text_center():
    # t = Text("some text a few words", border=True)
    t = Text(
        "some text a few good words that print WRAP to the great LINE",
        max_width=2.0,
    )
    canvas.add(t)
    d = Dot(t.center)
    canvas.add(d)
    canvas.snapshot()


# text_center()


def line_scalar():
    l1 = Line()
    l2 = Line().shift(DOWN).scale(2)
    canvas.add(l1, l2)
    canvas.snapshot()


# line_scalar()


def tip_scalar():
    a = Arrow(stroke_width=2.0, stroke_color=GREEN).scale(2)
    canvas.add(a)
    a = Arrow(tip_scalar=0.5).shift(DOWN)

    canvas.add(a)
    canvas.snapshot()


# tip_scalar()


def labeled_dot():
    l1 = LabeledDot(label=Text("hi"))
    canvas.add(l1)
    canvas.snapshot()


# labeled_dot()


def nested_group():
    t = Text("dog")
    t1 = Text("cat").shift(RIGHT)
    t2 = Text("mouse").move_to(t1, UP)
    g = Group(t)
    # g.add(t1)
    g1 = Group(t1)
    g1.add(t2)
    g.add(g1)

    canvas.add(g)
    canvas.snapshot()


# nested_group()


def rounded_rect():
    # correct, radius is allowed
    r = Rectangle(corner_radius=0.5 - 0.01)
    # incorrect, radius too large
    # r = Rectangle(corner_radius=0.5 + 0.01)
    canvas.add(r)
    canvas.snapshot()


# rounded_rect()


def rounded_shapes():
    r = RegularPolygon(n=6, corner_radius=0.3)
    t = Triangle(corner_radius=0.1, fill_color=BLUE).shift(LEFT * 2)
    canvas.add(t)
    canvas.add(r)

    # currently not handled, see `rounded_corners` function in `Polygon`
    reverse_t = Polygon(
        vertices=[[0, 1, 0], [1, 0, 0], [-1, 0, 0]], corner_radius=0.1
    ).shift(RIGHT * 2)
    canvas.add(reverse_t)
    canvas.snapshot()


# rounded_shapes()


def arc_between():
    a = Arc.from_points([-0.9, 0.5, 0], [0, -1, 0])
    canvas.add(a)
    canvas.snapshot()


# arc_between()


def arc_along_square():
    s = Square().shift(LEFT + 2 * UP)
    a = Arc.from_points(s.get_corner(DL), s.get_corner(DR))
    canvas.add(s, a)
    canvas.snapshot()


# arc_along_square()


def surround_shapes():
    c = Circle()
    c_rect = SurroundingRectangle(c)
    canvas.add(c, c_rect)

    t = Text("hey").shift(UR * 1.2)
    t_rect = SurroundingRectangle(t)
    canvas.add(t, t_rect)
    canvas.snapshot()


# surround_shapes()


def cross_square():
    s = Square()
    c = Cross(s)

    canvas.add(s, c)
    canvas.snapshot()


# cross_square()


def cross_text():
    t = Text("2 > 7")
    c = Cross(t, stroke_opacity=0.6, scale_factor=0.4)
    canvas.add(t, c)
    canvas.snapshot()


# cross_text()


# ChatGPT generated, edited so that "get_start" => start, "get_end" => end
# Concern: The changes I'm making in the API will decrease generation quality
def vector_addition():
    vector1 = Arrow(
        start=LEFT * 2,
        end=UP * 2 + LEFT * 2,
        stroke_color=BLUE,
        stroke_width=2.0,
        tip_length=0.2,
    )
    vector1_label = Text("v1", color=BLUE).next_to(vector1.start, LEFT, buff=0.1)

    vector2 = Arrow(
        start=UP * 2 + LEFT * 2,
        end=UP * 2 + RIGHT * 2,
        stroke_color=GREEN,
        stroke_width=2.0,
        tip_length=0.2,
    )
    vector2_label = Text("v2", color=GREEN).next_to(vector2.end, RIGHT, buff=0.1)

    vectorSum = Arrow(
        start=LEFT * 2,
        end=UP * 2 + RIGHT * 2,
        stroke_color=RED,
        stroke_width=2.0,
        tip_length=0.2,
    )
    sum_label = Text("v1 + v2", color=RED).next_to(vectorSum.end, DOWN, buff=0.1)

    canvas.add(vector1)
    canvas.add(vector1_label)
    canvas.add(vector2)
    canvas.add(vector2_label)
    canvas.add(vectorSum)
    canvas.add(sum_label)

    canvas.snapshot()


# vector_addition()


# Cleaner version of above vector addition
def my_vector_addition():
    v1 = Arrow(start=LEFT * 2, end=UP * 2 + LEFT * 2, fill_color=BLUE)
    # Making the text use "color" vs the arrow use "fill_color" is a bit tough
    # FUTURE: Maybe every object can a default fill_color or stroke_color that gets set when color is passed in
    v1_label = v1.create_label("v1_label")

    v2 = Arrow(start=UP * 2 + LEFT * 2, end=UP * 2 + RIGHT * 2, fill_color=GREEN)
    v2_label = v2.create_label("v2")

    vsum = Arrow(start=LEFT * 2, end=UP * 2 + RIGHT * 2, fill_color=RED)
    vsum_label = vsum.create_label("v1 + v2 and more text to demo", opposite_side=True)
    canvas.add(v1, v1_label)
    canvas.add(v2, v2_label)
    canvas.add(vsum, vsum_label)

    canvas.snapshot()


# my_vector_addition()


def flipped_vector_label():
    v0 = Arrow().shift(UP * 3)
    label0 = v0.create_label("basic")

    canvas.add(v0, label0)
    v1 = Arrow(start=RIGHT * 2, end=DOWN * 2 + LEFT * 2, fill_color=RED)
    label1 = v1.create_label("x + y")
    canvas.add(v1, label1)
    v2 = Arrow(start=ORIGIN, end=UP + LEFT, fill_color=RED)
    label2 = v2.create_label("z + w")
    canvas.add(v2, label2)
    canvas.snapshot()


# flipped_vector_label()


def label_arrow_cases():
    v1 = Arrow(start=LEFT, end=RIGHT)
    canvas.add(v1.create_label("v1"))

    v2 = Arrow(start=ORIGIN + RIGHT * 0.1, end=UR)
    canvas.add(v2.create_label("v2 at PI/4"))

    v3 = Arrow(start=ORIGIN + UP * 0.1, end=UL)
    canvas.add(v3.create_label("v3 at 3PI/4"))

    v4 = Arrow(start=ORIGIN + LEFT * 0.1, end=DL)
    canvas.add(v4.create_label("v4"))

    v5 = Arrow(start=ORIGIN + DOWN * 0.1, end=DR)
    canvas.add(v5.create_label("v5"))

    v6 = Arrow(start=ORIGIN + DOWN * 0.2, end=DOWN - 0.01)
    canvas.add(v6.create_label("v6"))

    canvas.add(v1, v2, v3, v4, v5, v6)

    canvas.snapshot()


def rect_surrounding_circle():
    c = Circle()
    c_rect = SurroundingRectangle(c)
    c.shift(RIGHT)
    canvas.add(c, c_rect)
    canvas.snapshot()


# rect_surrounding_circle()


def single_letter_with_bg():
    letter = Text("h")
    l_rect = SurroundingRectangle(letter, fill_color=RED, fill_opacity=0.3)
    # must add surrounding rect directly so that letter shift includes it
    letter.add(l_rect)
    letter.shift(RIGHT * 3)
    canvas.add(letter)
    canvas.snapshot()


# single_letter_with_bg()


def arrow_next_to():
    s = Arrow()
    a = Arrow().rotate(PI)
    a.next_to(s)

    canvas.add(s, a)
    canvas.snapshot()


# arrow_next_to()


def double_arrow():
    a = Arrow(at_start=True, at_end=True)
    canvas.add(a)
    canvas.snapshot()


# double_arrow()


def text_rotation():
    a = Arrow(LEFT, UR)
    t = Text("hey there")
    t.next_to(a, UR, buff=0)
    g = Group(a, t)

    g2 = g.copy()
    canvas.add(g2)

    g.rotate(PI)
    canvas.add(g)
    canvas.snapshot()


# text_rotation()


def text_rotation_internals():
    # Used for figuring out what internals to use for text rotation
    o = Dot([0, 0, 0])
    to = Text("origin")
    canvas.add(to)
    l1 = Line(ORIGIN, UR)
    l2 = Line(ORIGIN, UL)
    canvas.add(l1, l2)
    dot1 = Dot(UR, fill_color=GREEN)
    dot2 = Dot(UR, fill_color=BLUE).rotate(PI / 4)
    canvas.add(dot1, dot2)
    t1 = Text("to rotate").shift(UR)
    t2 = Text("not rotate").shift(UR)
    t1.rotate(PI / 4)
    # t1.rotate(PI / 12)

    t2_center = Dot(t2.center, fill_color=YELLOW)
    t1_center = Dot(t1.center, fill_color=ORANGE)
    t1_ul = Dot(t1.svg_upper_left, fill_color=TEAL)
    canvas.add(t1_ul)
    canvas.add(t1_center, t2_center)
    canvas.add(o, t1, t2)
    canvas.snapshot()


# text_rotation_internals()


def vector_mirror_about():
    a_vec = np.array([2, 1, 0])
    a = Vector(a_vec)
    b_vec = np.array([0.5, 1, 0])
    b = Vector(b_vec)
    c_vec = mirror_vector(b_vec, a_vec)
    c = Vector(c_vec)
    canvas.add(a, b, c)
    canvas.snapshot()


# vector_mirror_about()


def test_draw():
    canvas = Canvas(CONFIG)
    canvas.add(Circle())
    canvas.draw()


# test_draw()


def vector_inputs():
    v = Vector(UL * 3)
    canvas.add(v)
    canvas.snapshot()


# vector_inputs()


def vgroup_ops():
    s = Square()
    r = Rectangle().shift(UP * 2)
    g = VGroup(s, r)
    g.rotate()
    g.set_color(BLUE)
    canvas.add(g)
    canvas.snapshot()


# vgroup_ops()


def row_and_col():
    squares = [Square(side_length=i / 10, stroke_opacity=i * 0.1) for i in range(9)]
    circles = [Circle(radius=i / 10, stroke_opacity=i * 0.1) for i in range(5)]
    s = VGroup(*squares).arrange()
    c = VGroup(*circles).arrange(direction=DOWN, aligned_edge=RIGHT)
    canvas.add(c, s)
    canvas.snapshot()


# row_and_col()


def text_add():
    hi = Text("hi", color=RED)
    there = Text("there ", color=BLUE)
    adder = Text("adder", color=GREEN)
    # there.next_to(hi)
    # group = Group(hi, there)
    # adder.next_to(group)
    # canvas.add(group, adder)
    result = hi + there + adder
    canvas.add(result)
    canvas.snapshot()


# text_add()


# Future: See setup_text_layout in textmobject.py and maybe investigate PIL font ascent
def text_bbox():
    t = Text("Garg is going to the mall today", max_width=2.0)
    # t = Text("ag")
    # t = Text("aa")
    t.shift(UP)
    for p in t.bounding_points:
        canvas.add(Dot(p))
    canvas.add(t)
    canvas.snapshot(crop=True)


# text_bbox()


def point_from_prop():
    c = Circle()
    p1 = Dot(c.point_from_proportion(0.5))
    p2 = Dot(c.point_from_proportion(0.25))
    canvas.add(c)
    canvas.add(p1, p2)

    canvas.snapshot()


# point_from_prop()


def dot_default_color():
    d = Dot()
    canvas.add(d)
    canvas.snapshot()


# dot_default_color()


def arrow_color():
    a = Arrow()
    a.set_color(GREEN).set_opacity(0.5)
    canvas.add(a)
    canvas.snapshot()


# arrow_color()


def arrange_in_grid():
    n = 24
    v = Group(
        *[
            Square(
                side_length=0.5 if i % 2 == 0 else 0.3,
                fill_color=BLUE,
                fill_opacity=i / n,
            )
            for i in range(n)
        ]
    )
    # v.arrange()
    v.arrange_in_grid(num_cols=6, buff_within_col=0.5, aligned_edge_within_row=DOWN)
    canvas.add(v)
    canvas.snapshot()


# arrange_in_grid()


def simplest_grid():
    n = 10
    s = Group(
        *[
            Square(side_length=i / n, fill_color=RED, fill_opacity=i / n)
            for i in range(1, n)
        ]
    )
    s.arrange_in_grid(num_rows=2, aligned_edge_within_row=DOWN)
    canvas.add(s)
    canvas.snapshot()


# simplest_grid()


def init_text_location():
    c = Circle()
    t = Text("hello world, that's a wrap this text i mean")
    canvas.add(c, t)
    canvas.snapshot()


# init_text_location()


def next_to_testing():
    c = Circle()
    r = Rectangle(height=1.5)
    c.next_to(r, direction=UR)
    canvas.add(c, r)
    canvas.snapshot()


# next_to_testing()


# removing aligned_edge in both these scenarios since
# c.move_to(r, aligned_edge=UP)
# is not much better than
# c.move_to(r).align_to(r, UP)
def move_to_testing():
    c = Circle()
    r = Rectangle(height=1.5).shift(RIGHT)
    c.move_to(r).align_to(r, UP)
    canvas.add(c, r)
    canvas.snapshot()


# move_to_testing()


def box_list():
    b = BoxList(
        *[Square(fill_color=RED, fill_opacity=i / 8).scale(0.2) for i in range(1, 9)]
    )
    b1 = BoxList(*[Text(str(i)) for i in range(5)]).shift(DOWN)
    canvas.add(b1)
    b2 = BoxList(Text("different"), Text("size")).shift(UP)
    canvas.add(b2)

    canvas.add(b)
    canvas.snapshot()


# box_list()


def align_to_buff():
    c = Circle()
    r = Rectangle(width=1.5)
    # c.align_to(r, UP, buff=0.2)
    c.align_to(r, RIGHT, buff=0.2)
    canvas.add(c, r)
    canvas.snapshot()


# align_to_buff()


def default_colors():
    # default fill color is blue, but can override it
    c = Circle(fill_color=RED)
    c_label = c.create_label("hi")
    canvas.add(c, c_label)

    # default fill color is white
    d = Dot().shift(RIGHT)
    canvas.add(d)

    # default fill color is white
    s = Square().next_to(c, LEFT, buff=1.0)
    canvas.add(s)

    # default overall color is white
    a = Arrow(start=s, end=c)
    canvas.add(a)

    # default stroke is white
    line = Line().shift(UP * 2)
    canvas.add(line)

    # default stroke is blue
    a = Arc().shift(RIGHT)
    canvas.add(a)

    c2 = Circle(stroke_color=ORANGE).shift(UP * 3)
    canvas.add(c2)

    canvas.snapshot()


# default_colors()


def fill_stroke():
    c1 = Circle(radius=0.2, fill_color=YELLOW)
    c1.add(c1.create_label("set fill", font_size=14))

    c2 = Circle(radius=0.2, fill_color=YELLOW, stroke_color=GREEN)
    c2.add(c2.create_label("set stroke and fill", font_size=14))

    c3 = Circle(radius=0.2, stroke_color=ORANGE)
    c3.add(c3.create_label("set stroke", font_size=14))

    c4 = Circle(radius=0.2)
    c4.add(c4.create_label("no set (use default)", font_size=14))

    circle_demos = BoxList(c1, c2, c3, c4, aligned_edge=DOWN).shift(LEFT)
    circle_demos.add(
        circle_demos.create_label("Ways to color a circle", max_width=4.0, buff=0.1)
    )

    canvas.add(circle_demos)
    canvas.snapshot()


# fill_stroke()


def grid_simple():
    g = VGroup(*[Square() for i in range(8)])
    g.arrange_in_grid(num_rows=2)
    canvas.add(g)
    canvas.snapshot()


# grid_simple()


def simple_group():
    g = Group(Square().shift(LEFT), Square(color=GREEN), Square().shift(RIGHT))
    canvas.add(g)
    canvas.snapshot()


# simple_group()


def simpler_group():
    g = Group(Circle())
    canvas.add(g)
    result = canvas.draw()
    print(result)
    # canvas.snapshot()


# simpler_group()


class TwoCircle(VGroup):
    def __init__(self):
        super().__init__()
        self.add(Circle())
        self.add(Circle(color=RED).scale(0.5))


def simple_vgroup_class():

    g = TwoCircle()
    canvas.add(g)
    result = canvas.draw()
    # print(result)
    metadata = canvas.draw()
    meta = json.loads(metadata)["metadata"]
    print(meta)
    # canvas.snapshot()


# simple_vgroup_class()


def y_axis_test():
    n = NumberPlane().scale(0.5).shift(LEFT + DOWN * 2)
    n.plot(lambda x: 2 * x + 1)
    n.scale(0.5)
    canvas.add(n)
    canvas.snapshot()


# y_axis_test()


def tree_test():
    g = Graph(
        vertices=[0, 1, 2, 3, 4],
        edges=[(0, 1), (0, 2), (2, 3), (2, 4)],
        include_vertex_labels=True,
        layout="tree",
        root_vertex=0,
    )
    g.align_to(canvas.left, edge=LEFT)
    canvas.add(g)

    canvas.snapshot()


# tree_test()


def arrow_pointer():
    c = Circle()
    a = Arrow.points_at(c, direction=LEFT)
    g1 = Group(c, a)
    c2 = Circle(color=RED)
    a2 = Arrow.points_at(c2, direction=UP + RIGHT, length=0.5, buff=0)
    g2 = Group(c2, a2)

    groups = Group(g1, g2).arrange()
    canvas.add(groups)
    title = Text("Italics", italics=True).shift(UP * 2)
    canvas.add(title)
    canvas.snapshot()


# arrow_pointer()


def next_to_and_align():
    s = Square()
    t = Text("This is the title")
    # s.next_to(t, DOWN).align_to(t, LEFT)
    # since this is so common i'm making a new syntax for it
    # s.next_to(t, DOWN, aligned_edge=LEFT) or more simply
    s.next_to(t, DOWN, LEFT)
    canvas.add(s, t)
    canvas.snapshot()


# next_to_and_align()


def introduce_lambda():
    lamb = LambdaWithEyes()
    lamb.move_to(ORIGIN)
    canvas.add(lamb)
    canvas.snapshot()


# introduce_lambda()


def simple_italics():
    t1 = (
        Text("Two things I really like about Manim are its ")
        + Text("relative positioning commands ", italics=True)
        + Text("and its ")
        + Text("spatial transformations", italics=True)
    ).shift(LEFT * 3)
    canvas.add(t1)
    canvas.snapshot()


# simple_italics()


def box_list_down():
    c = Circle(color=RED, opacity=0.5)
    s = Square(color=BLUE, opacity=0.5)
    t = Triangle()
    b1 = BoxList(c, s, t, direction=DOWN).shift(LEFT)
    b2 = BoxList(c.copy(), s.copy(), t.copy(), direction=UP)
    g1 = Group(b1, b2).arrange().scale(0.5)
    t1 = Text("Vertical flow").next_to(g1, UP)
    canvas.add(g1, t1)
    b3 = BoxList(c.copy(), s.copy(), t.copy(), direction=RIGHT).shift(LEFT)
    b4 = BoxList(c.copy(), s.copy(), t.copy(), direction=LEFT)
    g2 = Group(b3, b4).arrange(direction=DOWN).next_to(g1)
    t2 = Text("Horizontal flow").next_to(g2, UP)
    canvas.add(g2, t2)
    # b = BoxList(c, s)
    canvas.snapshot()


# box_list_down()


def fill_opacity():
    c = Circle(fill_color=GREEN, fill_opacity=0.0)
    canvas.add(c)
    canvas.snapshot()


# fill_opacity()


# Bug: The spacing is different locally and in the browser on this example, an extra space after "its" in browser
def text_spacing():
    t1 = Text("The spacing is different locally and in the browser on this example")
    t1_rect = SurroundingRectangle(t1, buff=0)
    canvas.add(t1, t1_rect)
    canvas.snapshot()


# text_spacing()


def to_edge_demo():
    c = Circle()
    t = Text("Title").to_edge(UP)
    label = Text("label").to_edge(LEFT, buff=0)
    canvas.add(t, c, label)
    canvas.snapshot()


# to_edge_demo()


def nline_stretch():
    y_axis = NumberLine(color=GRAY)
    y_axis.stretch(0.5, dim=0)
    y_axis.rotate(PI / 8)
    canvas.add(y_axis)
    canvas.snapshot(crop=True)


# nline_stretch()


def global_font_style():
    canvas.set_global_text_styles(color=RED, font_family="Roboto")
    t1 = Text("red")

    t2 = Text("blue", color=BLUE)
    t3 = Text("red again")
    canvas.add(*Group(t1, t2, t3).arrange())
    canvas.snapshot(ignore_bg=True)


# global_font_style()
def close_to_demo():
    vertices = [0, 1, 2, 3, 4]
    edges = [(0, 1), (1, 2), (1, 3), (2, 3), (3, 0), (3, 4)]
    g = Graph(
        vertices=vertices, edges=edges, layout="circular", include_vertex_labels=True
    )
    labels = Group()
    for v in g.vertices.values():
        t = Text("∞").close_to(v, g.get_family())
        labels.add(t)
    canvas.add(g, labels)
    canvas.snapshot()


# close_to_demo()


def label_line():
    line = Line()
    l1_label = line.create_label("l1")
    canvas.add(line, l1_label)
    canvas.snapshot()


# label_line()
