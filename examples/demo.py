from smanim import *


def squareTest():
    s = Square()
    canvas.add(s)
    canvas.snapshot(preview=True)


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
    line = Line(s, r, buff=0.2, dashed=True)
    canvas.add(s)
    canvas.add(r)
    canvas.add(line)
    canvas.snapshot(preview=True)


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
    line = Line(LEFT, RIGHT)
    canvas.add(line)
    s = Square()
    canvas.add(s)
    # TODO: & symbol does not work
    # t = Text("hi there the terminal is beautiful and DARK like the night SKY")
    t = Text(
        "hi there the terminal is beautiful and dark like the night sky",
        fill_opacity=0.3,
    ).rotate()
    t.next_to(s)
    canvas.add(t)
    canvas.snapshot(preview=True)


# textTest()
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
    g = Group(s, s1, line)
    g.scale(0.5)
    canvas.add(g)
    canvas.snapshot(preview=True)


# scaleGroup1()


# test scale group and test border rotation
# TODO: having to specify about_point=None is not intuitive for "scaling in place"
def scaleGroup():
    g = Group()
    t = (
        Text("hi there", border=True)
        .shift(UR * 2)
        .rotate(-PI / 2)
        .scale(2, about_point=None)
    )
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


scaleGroup()
