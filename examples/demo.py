from smanim import *


class Test(Canvas):
    def construct(self):
        s = Square(side_length=0.5)
        self.add(s)

        r = Rectangle(2, 4)
        self.add(r)
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
