from smanim import *


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


class PolygonTest(Canvas):
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
        # it's recommended to set the fill using the `fill_color` attr
        # fill opacity must also be set and is not a default
        s2 = Square(fill_color=RED, fill_opacity=1.0).shift(LEFT * 1.5)
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


# canvas = AlignmentTest()
# canvas.construct()

# canvas = PosTest()
# canvas.construct()

# canvas = StrokeFillTest()
# canvas.construct()


# canvas = StrokeFamilyTest()
# canvas.construct()

canvas = GroupTest()
canvas.construct()

# canvas = ColorTest()
# canvas.construct()
