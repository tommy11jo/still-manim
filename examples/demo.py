from smanim import *


class Test(Canvas):
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


canvas = Test()
canvas.construct()
