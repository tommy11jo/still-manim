from pathlib import Path
from smanim import *
from smanim.utils.space_ops import mirror_vector

# config = Config(save_file_dir=Path(__file__).parent / "media")
CONFIG.save_file_dir = Path(__file__).parent / "media"
canvas = Canvas(CONFIG)


def simple_square():
    s = Square()
    canvas.add(s)
    canvas.snapshot(preview=True)


# simple_square()


def simple_triangle():
    t = Triangle()
    canvas.add(t)
    canvas.snapshot(preview=True)


# simple_triangle()


def square_stroke():
    # this shows that SVG draws stroke equally on inner and outer border
    s1 = Square(stroke_color=BLUE, stroke_width=30).shift(LEFT * 2)
    canvas.add(s1)
    canvas.snapshot(preview=True)


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

    canvas.snapshot(preview=True)
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
    canvas.snapshot(preview=True)


# align_square()


def rotate_hexagon():
    p = RegularPolygon()
    p.rotate(PI / 30)
    canvas.add(p)
    canvas.snapshot(preview=True)


# rotate_hexagon()


def position_square():
    s = Square()
    s.set_position([4, 2])
    # s.set_x(4)
    # s.set_y(3)
    canvas.add(s)

    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


# polygon_bring_to_back()


def square_to_rect_line():
    s = Square().shift(UL)
    r = Rectangle().shift(DR * 2)
    line = Line(s, r, dashed=True)
    canvas.add(s)
    canvas.add(r)
    canvas.add(line)
    canvas.snapshot(preview=True)


# square_to_rect_line()


def square_to_square_arrow():
    left = Square().shift(LEFT * 2)
    right = Square().shift(RIGHT * 2)
    arrow = Arrow(left, right)
    canvas.add(arrow, left, right)
    canvas.snapshot(preview=True)


# square_to_square_arrow()


def dashed_arrow():
    s = Square().shift(UL)
    r = Rectangle().shift(DR * 2)
    arrow = Arrow(s, r, buff=0.2, dashed=True)
    canvas.add(s, r, arrow)

    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


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

    canvas.snapshot(preview=True)


# arc_to_arc_arrow()


def brace_on_text_and_shapes():
    c = Circle()
    b = Brace(c)
    g = VGroup(c, b).shift(LEFT * 3)
    canvas.add(g)

    l1 = Line()
    b1 = Brace(l1)
    g1 = VGroup(l1, b1).shift(UP * 2)
    canvas.add(g1)
    t = Text("brace for it")
    # Demo of how brace location is determined from bounding points
    for d in t.bounding_points:
        canvas.add(Dot(d))
    b2 = Brace(t, buff=0.0)
    # Must use Group due to Text not being a VMobject (i.e. an object made of bezier curves only)
    g2 = Group(t, b2)
    canvas.add(g2)
    canvas.snapshot(preview=True)


# brace_on_text_and_shapes()


def brace_between_test():
    s1 = Square().shift(LEFT * 2)
    canvas.add(s1)
    s2 = Square().shift(RIGHT * 2)
    canvas.add(s2)
    b = Brace.from_positions(s1, s2, color=RED)
    canvas.add(b)
    canvas.snapshot(preview=True)


# brace_between_test()


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
    canvas.snapshot(preview=True)


# wrapping_text()


def text_with_html_chars():
    t = Text("&&hi&&")
    canvas.add(t)
    canvas.snapshot(preview=True)


# text_with_html_chars()


def arrow_scale():
    # a = Arrow(LEFT, RIGHT)
    a = Arrow(DL, UR)
    # a.scale(2)
    a.scale(0.5)
    canvas.add(a)
    canvas.snapshot(preview=True)


# arrow_scale()


def submobject_scale():
    s = Square().shift(UR * 3)
    s.add(Square().shift(UR))
    s.scale(0.6)
    canvas.add(s)
    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


# text_center()


def line_scalar():
    l1 = Line()
    l2 = Line().shift(DOWN).scale(2)
    canvas.add(l1, l2)
    canvas.snapshot(preview=True)


# line_scalar()


def tip_scalar():
    a = Arrow(stroke_width=2.0, stroke_color=GREEN).scale(2)
    canvas.add(a)
    a = Arrow(tip_scalar=0.5).shift(DOWN)

    canvas.add(a)
    canvas.snapshot(preview=True)


# tip_scalar()


def labeled_dot():
    l1 = LabeledDot(label=Text("hi"))
    canvas.add(l1)
    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


# nested_group()


def rounded_rect():
    # correct, radius is allowed
    r = Rectangle(corner_radius=0.5 - 0.01)
    # incorrect, radius too large
    # r = Rectangle(corner_radius=0.5 + 0.01)
    canvas.add(r)
    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


# rounded_shapes()


def arc_between():
    a = Arc.from_points([-0.9, 0.5, 0], [0, -1, 0])
    canvas.add(a)
    canvas.snapshot(preview=True)


# arc_between()


def arc_along_square():
    s = Square().shift(LEFT + 2 * UP)
    a = Arc.from_points(s.get_corner(DL), s.get_corner(DR))
    canvas.add(s, a)
    canvas.snapshot(preview=True)


# arc_along_square()


def surround_shapes():
    c = Circle()
    c.add_surrounding_rect()
    canvas.add(c)

    t = Text("hey").shift(UR * 1.2)
    t.add_surrounding_rect(corner_radius=0.1)
    canvas.add(t)
    canvas.snapshot(preview=True)


# surround_shapes()


def cross_square():
    s = Square()
    c = Cross(s)

    canvas.add(s, c)
    canvas.snapshot(preview=True)


# cross_square()


def cross_text():
    t = Text("2 > 7")
    c = Cross(t, stroke_opacity=0.6, scale_factor=0.4)
    canvas.add(t, c)
    canvas.snapshot(preview=True)


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

    canvas.snapshot(preview=True)


# vector_addition()


# Cleaner version of above vector addition
def my_vector_addition():
    v1 = Arrow(start=LEFT * 2, end=UP * 2 + LEFT * 2, fill_color=BLUE)
    # Making the text use "color" vs the arrow use "fill_color" is a bit tough
    # FUTURE: Maybe every object can a default fill_color or stroke_color that gets set when color is passed in
    v1_label = Text("v1 label")
    v1.add_label(v1_label)

    v2 = Arrow(start=UP * 2 + LEFT * 2, end=UP * 2 + RIGHT * 2, fill_color=GREEN)
    v2_label = Text("v2")
    v2.add_label(v2_label)

    vsum = Arrow(start=LEFT * 2, end=UP * 2 + RIGHT * 2, fill_color=RED)
    vsum_label = Text("v1 + v2 and more text to demo")
    vsum.add_label(vsum_label, opposite_side=True)
    canvas.add(v1, v1_label)
    canvas.add(v2, v2_label)
    canvas.add(vsum, vsum_label)

    canvas.snapshot(preview=True)


# my_vector_addition()


def flipped_vector_label():
    v0 = Arrow().shift(UP * 3)
    label0 = Text("basic")
    v0.add_label(label0)

    canvas.add(v0)
    v1 = Arrow(start=RIGHT * 2, end=DOWN * 2 + LEFT * 2, fill_color=RED)
    label1 = Text("x + y")
    v1.add_label(label1)
    canvas.add(v1)
    v2 = Arrow(start=ORIGIN, end=UP + LEFT, fill_color=RED)
    label2 = Text("z + w")
    v2.add_label(label2)
    canvas.add(v2)
    canvas.snapshot(preview=True)


# flipped_vector_label()


def label_arrow_cases():
    v1 = Arrow(start=LEFT, end=RIGHT)
    v1.add_label(Text("v1"))

    v2 = Arrow(start=ORIGIN + RIGHT * 0.1, end=UR)
    v2.add_label(Text("v2 at PI/4"))

    v3 = Arrow(start=ORIGIN + UP * 0.1, end=UL)
    v3.add_label(Text("v3 at 3PI/4"))

    v4 = Arrow(start=ORIGIN + LEFT * 0.1, end=DL)
    v4.add_label(Text("v4"))

    v5 = Arrow(start=ORIGIN + DOWN * 0.1, end=DR)
    v5.add_label(Text("v5"))

    v6 = Arrow(start=ORIGIN + DOWN * 0.2, end=DOWN - 0.01)
    v6.add_label(Text("v6"))

    canvas.add(v1, v2, v3, v4, v5, v6)

    canvas.snapshot(preview=True)


# label_arrow_cases()


def surrounding_rect_mob_with_submobs():
    s = Square()
    t = Text("Text width automatically")

    s.add_label(t)
    s.add_surrounding_rect()

    t.add_surrounding_rect(stroke_color=RED, z_index=20)
    canvas.add(s)
    canvas.snapshot(preview=True)


# surrounding_rect_mob_with_submobs()


def reactive_surrounding_rect():
    t1 = Text("water bottle").shift(UP)
    t1.add_surrounding_rect()
    canvas.add(t1)
    t1.rotate(PI / 6)
    r = Rectangle(width=3.0).shift(LEFT * 4)
    # takes 0.05 seconds for `wrap_text` originally
    t2 = Text(
        "Text width automatically set to rect width and should wrap accordingly. Text width automatically set to rect width and should wrap accordingly",
    )
    t2.add_surrounding_rect(fill_color=RED, fill_opacity=0.3, corner_radius=0.2)

    # takes 0.08 seconds for `wrap_text` during stretching
    t2.stretch_to_fit_width(r.width)
    t2.next_to(r, DOWN, buff=0.1)
    canvas.add(r, t2)
    canvas.snapshot(preview=True)


# I'm mostly timing this to see speed of text wrapping (which is a bit janky)
# start_time = time.time()
# reactive_surrounding_rect()

# end_time = time.time()
# print("total time", end_time - start_time)
# locally this takes 0.09 seconds, will it be similar in browser env?
# https://pyodide.org/en/stable/project/roadmap.html
# pyodide is typically 3-5x slower so between 0.3 to 0.5 seconds + js overhead to load a basic diagram with text right now
# p5.js load time is also like 0.5 seconds for basic things


def rect_surrounding_circle():
    c = Circle()
    c.add_surrounding_rect()
    c.shift(RIGHT)
    canvas.add(c)
    canvas.snapshot(preview=True)


# rect_surrounding_circle()


def single_letter_with_bg():
    letter = Text("h")
    letter.add_surrounding_rect(fill_color=RED, fill_opacity=0.3)
    # Surrounding rect keeps up even after shift
    letter.shift(RIGHT * 3)
    canvas.add(letter)
    canvas.snapshot(preview=True)


# single_letter_with_bg()


def arrow_next_to():
    s = Arrow()
    a = Arrow().rotate(PI)
    a.next_to(s)

    canvas.add(s, a)
    canvas.snapshot(preview=True)


# arrow_next_to()


def double_arrow():
    a = Arrow(at_start=True, at_end=True)
    canvas.add(a)
    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


# text_rotation_internals()


def vector_mirror_about():
    a_vec = np.array([2, 1, 0])
    a = Vector(a_vec)
    b_vec = np.array([0.5, 1, 0])
    b = Vector(b_vec)
    c_vec = mirror_vector(b_vec, a_vec)
    c = Vector(c_vec)
    canvas.add(a, b, c)
    canvas.snapshot(preview=True)


# vector_mirror_about()


def test_draw():
    canvas = Canvas(CONFIG)
    canvas.add(Circle())
    canvas.draw()


# test_draw()


def vector_inputs():
    v = Vector(UL * 3)
    canvas.add(v)
    canvas.snapshot(preview=True)


# vector_inputs()


def vgroup_ops():
    s = Square()
    r = Rectangle().shift(UP * 2)
    g = VGroup(s, r)
    g.rotate()
    g.set_color(BLUE)
    canvas.add(g)
    canvas.snapshot(preview=True)


# vgroup_ops()


def row_and_col():
    squares = [Square(side_length=i / 10, stroke_opacity=i * 0.1) for i in range(9)]
    circles = [Circle(radius=i / 10, stroke_opacity=i * 0.1) for i in range(5)]
    s = VGroup(*squares).arrange()
    c = VGroup(*circles).arrange(direction=DOWN, aligned_edge=RIGHT)
    canvas.add(c, s)
    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True, crop=True)


# text_bbox()


def point_from_prop():
    c = Circle()
    p1 = Dot(c.point_from_proportion(0.5))
    p2 = Dot(c.point_from_proportion(0.25))
    canvas.add(c)
    canvas.add(p1, p2)

    canvas.snapshot(preview=True)


# point_from_prop()


def dot_default_color():
    d = Dot()
    canvas.add(d)
    canvas.snapshot(preview=True)


# dot_default_color()


def arrow_color():
    a = Arrow()
    a.set_color(GREEN).set_opacity(0.5)
    canvas.add(a)
    canvas.snapshot(preview=True)


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
    v.arrange_in_grid(cols=6, buff_within_col=0.5, row_aligned_edge=DOWN)
    canvas.add(v)
    canvas.snapshot(preview=True)


# arrange_in_grid()


def simplest_grid():
    n = 10
    s = Group(
        *[
            Square(side_length=i / n, fill_color=RED, fill_opacity=i / n)
            for i in range(1, n)
        ]
    )
    s.arrange_in_grid(rows=2, row_aligned_edge=DOWN)
    canvas.add(s)
    canvas.snapshot(preview=True)


# simplest_grid()


def init_text_location():
    c = Circle()
    t = Text("hello world, that's a wrap this text i mean")
    canvas.add(c, t)
    canvas.snapshot(preview=True)


# init_text_location()


def next_to_testing():
    c = Circle()
    r = Rectangle(height=1.5)
    c.next_to(r, direction=UR)
    canvas.add(c, r)
    canvas.snapshot(preview=True)


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
    canvas.snapshot(preview=True)


# move_to_testing()


def labeled_brace():
    # c = Circle()
    # l1 = LabeledBrace(c, label=Text("hi there"), direction=RIGHT)
    # canvas.add(c, l1)

    r = Rectangle().shift(DOWN)
    l2 = LabeledBrace.from_positions(
        start=r.get_corner(DL),
        end=r.get_corner(UR),
        label=Text("First", font_size=10),
        label_buff=0,
    )
    r2 = Rectangle().rotate(PI / 6).shift(UP * 1.5)
    text = Text("second", font_size=10)
    l3 = LabeledBrace.from_positions(
        r2.vertices[0], r2.vertices[2], label=text, label_buff=0
    )
    canvas.add(r2, l3)

    canvas.add(r, l2)
    canvas.snapshot(preview=True)


# labeled_brace()


def brace_span():
    c = Circle()
    b = Brace.from_mobject_edge(c, UP)
    canvas.add(c, b)

    s = Square().shift(UR * 3)
    b1 = LabeledBrace.from_mobject_edge(s, LEFT, label=Text("left"))
    canvas.add(s, b1)
    canvas.snapshot(preview=True)


# brace_span()


def box_list():
    b = BoxList(
        *[Square(fill_color=RED, fill_opacity=i / 8).scale(0.2) for i in range(1, 9)]
    )
    b1 = BoxList(*[Text(str(i)) for i in range(5)]).shift(DOWN)
    canvas.add(b1)
    b2 = BoxList(Text("different"), Text("size")).shift(UP)
    canvas.add(b2)

    canvas.add(b)
    canvas.snapshot(preview=True)


# box_list()


def align_to_buff():
    c = Circle()
    r = Rectangle(width=1.5)
    # c.align_to(r, UP, buff=0.2)
    c.align_to(r, RIGHT, buff=0.2)
    canvas.add(c, r)
    canvas.snapshot(preview=True)


# align_to_buff()


def default_colors():
    # default fill color is blue, but can override it
    c = Circle(fill_color=RED)
    c.add_label(Text("hi"))
    canvas.add(c)

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
    l = Line().shift(UP * 2)
    canvas.add(l)

    # default stroke is blue
    a = Arc().shift(RIGHT)
    canvas.add(a)

    c2 = Circle(stroke_color=ORANGE).shift(UP * 3)
    canvas.add(c2)

    canvas.snapshot(preview=True)


# default_colors()


def fill_stroke():
    # create a way to use default text size for a duration
    # canvas.config.set_font_size(16)
    c1 = Circle(radius=0.2, fill_color=YELLOW).add_label(Text("set fill", font_size=14))
    c2 = Circle(radius=0.2, fill_color=YELLOW, stroke_color=GREEN).add_label(
        Text("set stroke and fill", font_size=14)
    )
    c3 = Circle(radius=0.2, stroke_color=ORANGE).add_label(
        Text("set stroke", font_size=14)
    )
    c4 = Circle(radius=0.2).add_label(Text("no set (use default)", font_size=14))
    circle_demos = BoxList(c1, c2, c3, c4, aligned_edge=DOWN).shift(LEFT)

    circle_demos.add_label(Text("Ways to color a circle"), width=4.0, buff=0.1)

    canvas.add(circle_demos)

    canvas.snapshot(preview=True)


# fill_stroke()


# TODO: why doesn't this work in browser but it works locally?
# g[4].set_stroke(color=ORANGE)
def grid_simple():
    g = VGroup(*[Square() for i in range(8)]).arrange_in_grid(rows=2)
    canvas.add(g)
    canvas.snapshot(preview=True)


grid_simple()
