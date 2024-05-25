from smanim import *

c = Circle(stroke_color=RED)
t = Text("Hello World")
t.next_to(c, UP)
canvas.add(c, t)
canvas.snapshot()
