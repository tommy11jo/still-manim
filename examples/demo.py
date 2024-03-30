from smanim import *


class SquareTest(Canvas):
    def construct(self):
        s = Square()
        self.add(s)
        self.snapshot(preview=True)


class TriangleTest(Canvas):
    def construct(self):
        t = Triangle()
        self.add(t)
        self.snapshot(preview=True)


class StrokeTest(Canvas):
    def construct(self):
        s = Square()
        self.add(s)
        # this shows that SVG draws stroke equally on inner and outer border
        s1 = Square(stroke_color=BLUE, stroke_width=30).shift(LEFT * 2)
        self.add(s1)
        self.snapshot(preview=True)


class AlignmentTest(Canvas):
    def construct(self):
        s = Square(side_length=0.5)
        self.add(s)

        r = Rectangle(1, 2)
        s.next_to(r, DOWN, aligned_edge=RIGHT)
        self.add(r)

        t = Triangle()
        t.next_to(s, RIGHT, aligned_edge=DOWN)
        self.add(t)

        self.snapshot(preview=True)
        # self.add(s)
        # self.snapshot()

        # c = Circle()
        # self.add(c)
        # c.next_to(s)
        # c.shift(RIGHT)

        # a = Arrow(s, c)
        # t = Text("hi")
        # self.add(a)


class RotateTest(Canvas):
    def construct(self):
        p = RegularPolygon()
        p.rotate(PI / 30)
        self.add(p)
        self.snapshot(preview=True)


class PosTest(Canvas):
    def construct(self):
        s = Square()
        s.set_position([4, 2])
        # s.set_x(4)
        # s.set_y(3)
        self.add(s)

        self.snapshot(preview=True)


class StrokeFillTest(Canvas):
    def construct(self):
        s1 = Square(color=RED)
        s1.set_stroke(ORANGE)
        # now, the stroke will show but the fill will not, since stroke shows by default
        # self.add(s1)
        # self.snapshot(preview=True)
        s2 = Square(fill_color=RED).shift(LEFT * 1.5)
        self.add(s2)

        s3 = Square(side_length=2, color=BLUE).shift(DOWN)
        # setting the fill does not override the BLUE stroke
        s3.set_fill(GREEN)

        # sets both fill and stroke color/opacity
        # s1.set_color(RED, opacity=1.0)
        self.add(s3)
        self.add(s1)
        # s1.add_to_front(s2)
        # self.add_to_back(s2)
        self.snapshot(preview=True)


class StrokeFamilyTest(Canvas):
    def construct(self):
        s1 = Square(fill_color=RED)
        s2 = Square().shift(LEFT)
        s3 = Square().shift(DOWN)
        s4 = Rectangle().shift(UP * 2)
        s2.add(s4)
        s1.add(s2, s3)
        # s1.set_stroke(ORANGE, family=True)
        s1.set_stroke(ORANGE, family=False)
        self.add(s1)
        self.snapshot(preview=True)


class GroupTest(Canvas):
    def construct(self):
        s1 = Square()
        s2 = Square().shift(LEFT)
        s3 = Square().shift(RIGHT)
        s3.set_fill(RED)
        s2.add(s3)
        v = VGroup(s1, s2)
        # v.set_fill(GREEN)
        v.set_stroke(BLUE)
        self.add(v)
        self.snapshot(preview=True)


# z-index and vgroup indexing
class ZIndexTest(Canvas):
    def construct(self):
        s1 = Square()
        s2 = Square().shift(LEFT)
        # s2 = Square(z_index=-1).shift(LEFT)
        v = VGroup(s1, s2)
        v[0].set_stroke(YELLOW)
        self.add(v)
        self.snapshot(preview=True)


class ColorTest(Canvas):
    def construct(self):
        # s = Square(stroke_color=GREEN)
        s = Square()
        self.add(s)
        r = Rectangle()
        r.set_fill(YELLOW)
        self.add(r)

        self.snapshot(preview=True)


class LineTest(Canvas):
    def construct(self):
        s = Square().shift(UL)
        r = Rectangle().shift(DR * 3)
        line = Line(s, r, buff=0.2, dashed=True)
        self.add(s)
        self.add(r)
        self.add(line)
        self.snapshot(preview=True)


class ArrowTest(Canvas):
    def construct(self):
        # s = Square().shift(UL)
        # r = Rectangle().shift(DR * 3)
        # arrow = Arrow(s, r, buff=0.2, dashed=True)
        # self.add(s)
        # self.add(r)
        # self.add(arrow)

        # unlike arrows, lines don't have automatic buff
        # pos1 = LEFT * 2
        pos1 = LEFT * 2
        # pos2 = RIGHT * 2
        pos2 = UP * 1 + RIGHT * 2
        s = Square().shift(pos1)
        self.add(s)
        s1 = Square().shift(pos2)
        self.add(s1)
        # a = Line(s1, s)
        a = Arrow(s, s1)
        self.add(a)

        # t = Triangle()
        # self.add(t)
        # a = Arrow(LEFT, RIGHT)
        # a = ArrowTriangleFilledTip()
        # self.add(a)
        self.snapshot(preview=True)


class ArcTest(Canvas):
    def construct(self):
        arc = Arc()
        self.add(arc)
        circle = Circle(fill_color=BLUE)
        circle.next_to(arc)
        self.add(circle)

        arc2 = ArcBetweenPoints(UR, DR, radius=1)
        arc2.next_to(arc, LEFT)
        self.add(arc2)
        self.snapshot(preview=True)


class ArrowBetweenArcTest(Canvas):
    def construct(self):
        arc = Arc()
        self.add(arc)

        arc2 = ArcBetweenPoints(UR, DR, radius=1)
        arc2.shift(UL * 2)
        # example of janky bounding polygon debugging
        self.add(arc2)
        a = Arrow(arc, arc2)
        self.add(a)

        # demonstrates how the the start anchors of an unclosed shape are not enough for bounding polygon
        # must add one extra end anchor
        # see vmobject `points` setter for more
        for pt in arc2.bounding_points:
            d = Dot(np.array(pt), fill_color=BLUE)
            self.add(d)

        self.snapshot(preview=True)


class ArrowBetweenCircleTest(Canvas):
    def construct(self):
        circle = Circle().shift(LEFT)
        self.add(circle)

        circle2 = Circle().shift(UR * 2)
        self.add(circle2)
        a = Arrow(circle, circle2)
        self.add(a)
        self.snapshot(preview=True)


class BraceTest(Canvas):
    def construct(self):
        # c = Circle()
        # self.add(c)
        # b = Brace(c)
        # self.add(b)

        # d = Square().shift(UR * 3)
        # self.add(d)
        s1 = Square().shift(LEFT * 2)
        self.add(s1)
        s2 = Square().shift(RIGHT * 2)
        self.add(s2)
        # b = Line(s1, s2)
        # l1 = Line((0, 0, 0), (1, 0, 0))
        # b = Brace(l1)
        b = BraceBetween(s1, s2)
        self.add(b)
        self.snapshot(preview=True)


# canvas = SquareTest()
# canvas.construct()

# canvas = TriangleTest()
# canvas.construct()

# canvas = StrokeTest()
# canvas.construct()

# canvas = AlignmentTest()
# canvas.construct()

# canvas = RotateTest()
# canvas.construct()

# canvas = PosTest()
# canvas.construct()

# canvas = StrokeFillTest()
# canvas.construct()


# canvas = StrokeFamilyTest()
# canvas.construct()

# canvas = GroupTest()
# canvas.construct()

# canvas = ColorTest()
# canvas.construct()

# canvas = LineTest()
# canvas.construct()

# canvas = ArrowTest()
# canvas.construct()

# canvas = ArcTest()
# canvas.construct()

# canvas = ArrowBetweenArcTest()
# canvas.construct()

# canvas = ArrowBetweenCircleTest()
# canvas.construct()

canvas = BraceTest()
canvas.construct()
