from pathlib import Path
from smanim import *

config = Config(save_file_dir=Path(__file__).parent / "media")
canvas = Canvas(config)


def squareTest():
    s = Square()
    canvas.add(s)
    canvas.snapshot(preview=True)


# squareTest()


def triangleTest():
    t = Triangle()
    canvas.add(t)
    canvas.snapshot(preview=True)


def strokeTest():
    canvas.add(s)
    # this shows that SVG draws stroke equally on inner and outer border
    s1 = Square(stroke_color=BLUE, stroke_width=30).shift(LEFT * 2)
    canvas.add(s1)
    canvas.snapshot(preview=True)


def nextToTest():
    s = Square(side_length=0.5)
    canvas.add(s)

    r = Rectangle(1, 2)
    s.next_to(r, DOWN, aligned_edge=RIGHT)
    canvas.add(r)

    t = Triangle()
    t.next_to(s, RIGHT, aligned_edge=DOWN)
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


def alignToTest():
    s = Square(side_length=0.5)
    s1 = Square().scale(2)
    s.align_to(s1, edge=UP)
    canvas.add(s)
    canvas.add(s1)
    canvas.snapshot(preview=True)


# alignToTest()


def rotateTest():
    p = RegularPolygon()
    p.rotate(PI / 30)
    canvas.add(p)
    canvas.snapshot(preview=True)


def positionTest():
    s = Square()
    s.set_position([4, 2])
    # s.set_x(4)
    # s.set_y(3)
    canvas.add(s)

    canvas.snapshot(preview=True)


def strokeFillTest():
    s1 = Square(color=RED)
    s1.set_stroke(ORANGE)
    # now, the stroke will show but the fill will not, since stroke shows by default
    # canvas.add(s1)
    # canvas.snapshot(preview=True)
    s2 = Square(fill_color=RED).shift(LEFT * 1.5)
    canvas.add(s2)

    s3 = Square(side_length=2, color=BLUE).shift(DOWN)
    # setting the fill does not override the BLUE stroke
    s3.set_fill(GREEN)

    # sets both fill and stroke color/opacity
    # s1.set_color(RED, opacity=1.0)
    canvas.add(s3)
    canvas.add(s1)
    # s1.add_to_front(s2)
    # canvas.add_to_back(s2)
    canvas.snapshot(preview=True)


def strokeFamilyTest():
    s1 = Square(fill_color=RED)
    s2 = Square().shift(LEFT)
    s3 = Square().shift(DOWN)
    s4 = Rectangle().shift(UP * 2)
    s2.add(s4)
    s1.add(s2, s3)
    # s1.set_stroke(ORANGE, family=True)
    s1.set_stroke(ORANGE, family=False)
    canvas.add(s1)
    canvas.snapshot(preview=True)


def groupTest():
    s1 = Square()
    s2 = Square().shift(LEFT)
    s3 = Square().shift(RIGHT)
    s3.set_fill(RED)
    s2.add(s3)
    v = VGroup(s1, s2)
    # v.set_fill(GREEN)
    v.set_stroke(BLUE)
    canvas.add(v)
    canvas.snapshot(preview=True)


def zIndexTest():
    s1 = Square()
    s2 = Square().shift(LEFT)
    # s2 = Square(z_index=-1).shift(LEFT)
    v = VGroup(s1, s2)
    v[0].set_stroke(YELLOW)
    canvas.add(v)
    canvas.snapshot(preview=True)


def colorTest():
    # s = Square(stroke_color=GREEN)
    s = Square()
    canvas.add(s)
    r = Rectangle()
    r.set_fill(YELLOW)
    canvas.add(r)

    canvas.snapshot(preview=True)


def lineTest():
    s = Square().shift(UL)
    r = Rectangle().shift(DR * 3)
    line = Line(s, r, dashed=True)
    canvas.add(s)
    canvas.add(r)
    canvas.add(line)
    canvas.snapshot(preview=True)


# lineTest()


def simpleArrowTest():
    left = Square().shift(LEFT * 2)
    right = Square().shift(RIGHT * 2)
    arrow = Arrow(left, right)
    canvas.add(arrow, left, right)
    canvas.snapshot(preview=True)


# simpleArrowTest()


def arrowTest():
    # s = Square().shift(UL)
    # r = Rectangle().shift(DR * 3)
    # arrow = Arrow(s, r, buff=0.2, dashed=True)
    # canvas.add(s)
    # canvas.add(r)
    # canvas.add(arrow)

    # unlike arrows, lines don't have automatic buff
    # pos1 = LEFT * 2
    pos1 = LEFT * 2
    # pos2 = RIGHT * 2
    pos2 = UP * 1 + RIGHT * 2
    s = Square().shift(pos1)
    canvas.add(s)
    s1 = Square().shift(pos2)
    canvas.add(s1)
    # a = Line(s1, s)
    a = Arrow(s, s1)
    canvas.add(a)

    # t = Triangle()
    # canvas.add(t)
    # a = Arrow(LEFT, RIGHT)
    # a = ArrowTriangleFilledTip()
    # canvas.add(a)
    canvas.snapshot(preview=True)


# arrowTest()


def arcTest():
    arc = Arc()
    canvas.add(arc)
    circle = Circle(fill_color=BLUE)
    circle.next_to(arc)
    canvas.add(circle)

    arc2 = ArcBetweenPoints(UR, DR, radius=1)
    arc2.next_to(arc, LEFT)
    canvas.add(arc2)
    canvas.snapshot(preview=True)


def arrowBetweenTest():
    arc = Arc()
    canvas.add(arc)

    arc2 = ArcBetweenPoints(UR, DR, radius=1)
    arc2.shift(UL * 2)
    # example of janky bounding polygon debugging
    canvas.add(arc2)
    a = Arrow(arc, arc2)
    canvas.add(a)

    # demonstrates how the the start anchors of an unclosed shape are not enough for bounding polygon
    # must add one extra end anchor
    # see vmobject `points` setter for more
    for pt in arc2.bounding:
        d = Dot(np.array(pt), fill_color=BLUE)
        canvas.add(d)

    canvas.snapshot(preview=True)


def arrowBetweenCircleTest():
    circle = Circle().shift(LEFT)
    canvas.add(circle)

    circle2 = Circle().shift(UR * 2)
    canvas.add(circle2)
    a = Arrow(circle, circle2)
    canvas.add(a)
    canvas.snapshot(preview=True)


def braceTest():
    # c = Circle()
    # canvas.add(c)
    # b = Brace(c)
    # canvas.add(b)

    # d = Square().shift(UR * 3)
    # canvas.add(d)
    s1 = Square().shift(LEFT * 2)
    canvas.add(s1)
    s2 = Square().shift(RIGHT * 2)
    canvas.add(s2)
    # b = Line(s1, s2)
    # l1 = Line((0, 0, 0), (1, 0, 0))
    # b = Brace(l1)
    b = BraceBetween(s1, s2)
    canvas.add(b)
    canvas.snapshot(preview=True)


def textTest():
    s = Square()
    canvas.add(s)
    t = Text(
        "hi there the terminal is beautiful and DARK like the night SKY and now let's see if the heights are correct during text wrap and no i don't think it is working and it's not just the lines with CAPS that are the problem. Ok corrected.",
        max_width=2.0,
    )
    t = Text(
        "hi there the terminal is beautiful and DARK like the night SKY and now let's see if the heights are correct during text wrap and no i don't think it is working and it's not just the lines with CAPS that are the problem. Ok corrected."
    )
    # t = Text("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", max_width=2.0)
    # t = Text("dog aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", max_width=2.0)
    # t = Text(
    #     "hi there the terminal is beautiful and dark like the night sky",
    #     fill_opacity=0.3,
    # ).rotate()
    # t.next_to(s)
    canvas.add(t)
    canvas.snapshot(preview=True)


# textTest()
def textWithAmpersand():
    t = Text("&&hi&&")
    canvas.add(t)
    canvas.snapshot(preview=True)


# textWithAmpersand()


def textBbox():
    t = Text("hi there").shift(UR * 2)
    s = Square().shift(DL)
    canvas.add(s)
    canvas.add(t)
    a = Arrow(t, s)
    canvas.add(a)
    canvas.snapshot(preview=True)


# textBbox()
def arrowScale():
    # a = Arrow(LEFT, RIGHT)
    a = Arrow(DL, UR)
    # a.scale(2)
    a.scale(0.5)
    canvas.add(a)
    canvas.snapshot(preview=True)


# arrowScale()
def submobjectScale():
    s = Square().shift(UR * 3)
    s.add(Square().shift(UR))
    s.scale(0.6)
    canvas.add(s)
    canvas.snapshot(preview=True)


# submobjectScale()


def scaleGroup1():
    s = Square().shift(DL)
    # s1 = Square().shift(UR * 2)
    s1 = Text("hi there", border=True).shift(UR * 2)
    line = Line(s, s1)
    g = VGroup(s, s1, line)
    g.scale(0.5)
    canvas.add(g)
    canvas.snapshot(preview=True)


# scaleGroup1()


# test scale group and test border rotation
def scaleGroup():
    g = VGroup()
    t = Text("hi there", border=True).shift(UR * 2).rotate(-PI / 2).scale(2)
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


# scaleGroup()


def textCenter():
    # t = Text("some text a few words", border=True)
    t = Text(
        "some text a few good words that print WRAP to the great LINE",
        max_width=2.0,
        border=True,
    )
    canvas.add(t)
    d = Dot(t.get_center())
    canvas.add(d)
    canvas.snapshot(preview=True)


# textCenter()
def textWrapLongWord():

    t2 = Text(
        "Word in the middleThatIsDefinitelyLonger than the max width",
        max_width=1.0,
    )
    canvas.add(t2)
    canvas.snapshot(preview=True)


# textWrapLongWord()


def lineBetween():
    s = Square().shift(LEFT)
    c = Circle().shift(UR * 2)
    line = Line(s, c)
    canvas.add(s, c, line)
    d1 = Dot(line.start)
    d2 = Dot(line.end)
    canvas.add(d1, d2)
    canvas.snapshot(preview=True)


# lineBetween()


def lineScalar():
    l1 = Line()
    l2 = Line().shift(DOWN).scale(2)
    canvas.add(l1, l2)
    canvas.snapshot(preview=True)


# lineScalar()


def tipScalar():
    a = Arrow(stroke_width=2.0, stroke_color=GREEN).scale(2)
    canvas.add(a)
    a = Arrow(tip_scalar=0.5).shift(DOWN)

    canvas.add(a)
    canvas.snapshot(preview=True)


# tipScalar()


def labeledDot():
    l1 = LabeledDot(label=Text("hi", color=BLUE))
    canvas.add(l1)
    canvas.snapshot(preview=True)


# labeledDot()


def nestedGroup():
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


# nestedGroup()


def roundedRect():
    r = Rectangle(corner_radius=0.5)
    canvas.add(r)
    canvas.snapshot(preview=True)


# roundedRect()


def roundedShapes():
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


# roundedShapes()


def arcBetween():
    a = ArcBetweenPoints([-0.9, 0.5, 0], [0, -1, 0])
    canvas.add(a)
    canvas.snapshot(preview=True)


# arcBetween()


def arcNotCentered():
    s = Square().shift(LEFT + 2 * UP)
    a = ArcBetweenPoints(s.get_corner(DL), s.get_corner(DR))
    canvas.add(s, a)
    canvas.snapshot(preview=True)


# arcNotCentered()


def surroundShapes():
    c = Circle()
    s = SurroundingRectangle(c)
    canvas.add(c, s)

    t = Text("hey").shift(UR)
    s2 = SurroundingRectangle(t, corner_radius=0.1)
    canvas.add(t, s2)
    canvas.snapshot(preview=True)


# surroundShapes()


def crossSquare():
    s = Square()
    c = Cross(s)

    canvas.add(s, c)
    canvas.snapshot(preview=True)


# crossSquare()


def crossText():
    t = Text("2 > 7")
    c = Cross(t, stroke_opacity=0.6, scale_factor=0.4)
    canvas.add(t, c)
    canvas.snapshot(preview=True)


# crossText()
# ChatGPT generated, edited so that "get_start" => start, "get_end" => end
# Concern: The changes I'm making in the API will decrease generation quality
def vectorAddtion():
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


# vectorAddtion()


def myVectorAddtion():
    v1 = Arrow(start=LEFT * 2, end=UP * 2 + LEFT * 2, fill_color=BLUE)
    # Making the text use "color" vs the arrow use "fill_color" is a bit tough
    # FUTURE: Maybe every object can a default fill_color or stroke_color that gets set when color is passed in
    v1_label = Text("v1", color=BLUE)
    v1.add_label(v1_label)

    v2 = Arrow(start=UP * 2 + LEFT * 2, end=UP * 2 + RIGHT * 2, fill_color=GREEN)
    v2_label = Text("v2", color=GREEN)
    v2.add_label(v2_label)

    vsum = Arrow(start=LEFT * 2, end=UP * 2 + RIGHT * 2, fill_color=RED)
    vsum_label = Text("v1 + v2", color=RED)
    vsum.add_label(vsum_label, opposite_side=True)
    canvas.add(v1, v1_label)
    canvas.add(v2, v2_label)
    canvas.add(vsum, vsum_label)

    canvas.snapshot(preview=True)


# myVectorAddtion()


def flippedVectorLabel():
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


# flippedVectorLabel()


def defaultLabeling():
    s = Square()
    t = Text(
        "Text width automatically is set to square width and should wrap accordingly"
    )

    s.add_label(t)
    canvas.add(s)

    r = Rectangle(width=3.0).shift(LEFT * 4)
    t2 = Text("Text width automatically set to rect width and should wrap accordingly")
    t2 = Text(
        "Text width automatically set to rect width and should wrap accordingly",
        # max_width=3.0,
    ).scale(0.5)
    b = SurroundingRectangle(t2)
    canvas.add(b, r, t2)
    canvas.snapshot(preview=True)


# defaultLabeling()


# FUTURE: Idea of reactive elements is powerful
# Fow now, just surrounding rectangles are reactive
def reactiveSurroundingRect():
    t1 = Text("water bottle").shift(UP)
    t1.add_surrounding_rect()
    canvas.add(t1)
    t1.rotate(PI / 6)
    r = Rectangle(width=3.0).shift(LEFT * 4)
    # takes 0.05 seconds for `wrap_text` originally
    t2 = Text(
        "Text width automatically set to rect width and should wrap accordingly. Text width automatically set to rect width and should wrap accordingly",
    ).scale(1)
    t2.add_surrounding_rect(fill_color=RED, fill_opacity=0.3, corner_radius=0.2)
    # takes 0.08 seconds for `wrap_text` during stretching
    t2.stretch_to_fit_width(r.width)
    t2.next_to(r, DOWN, buff=0.1)
    canvas.add(r, t2)
    canvas.snapshot(preview=True)


# start_time = time.time()
# reactiveSurroundingRect()
# end_time = time.time()
# print("total time", end_time - start_time)
# locally this takes 0.09 seconds, will it be similar in browser env?
# https://pyodide.org/en/stable/project/roadmap.html
# pyodide is typically 3-5x slower so between 0.3 to 0.5 seconds + js overhead to load a basic diagram with text right now
# p5.js load time is also like 0.5 seconds for basic things


def surroundingRectOnCircle():
    c = Circle()
    c.add_surrounding_rect()
    canvas.add(c)
    canvas.snapshot(preview=True)


# surroundingRectOnCircle()


def singleLetterBg():
    letter = Text("h")
    letter.add_surrounding_rect()
    letter.shift(RIGHT * 3)
    canvas.add(letter)
    canvas.snapshot(preview=True)


# singleLetterBg()


def gracefulCornerRadiusError():
    r = Rectangle(corner_radius=3)
    canvas.add(r)
    canvas.snapshot(preview=True)


# gracefulCornerRadiusError()


def arrowNextTo():
    s = Arrow()
    a = Arrow().rotate(PI)
    a.next_to(s)

    canvas.add(s, a)
    canvas.snapshot(preview=True)


# arrowNextTo()


def doubleArrow():
    a = Arrow(at_start=True, at_end=True)
    canvas.add(a)
    canvas.snapshot(preview=True)


# doubleArrow()


# TODO: Need more natural rotation about a point for text
def textRotation():
    a = Arrow(LEFT, UR)
    t = Text("hey there")
    t.next_to(a, UR, buff=0)
    g = Group(a, t)

    g2 = g.copy()
    canvas.add(g2)

    g.rotate(PI)
    canvas.add(g)
    canvas.snapshot(preview=True)


# textRotation()
