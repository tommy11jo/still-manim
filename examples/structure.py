from smanim import *


# This is what the code will look like in the browser
# assume user will modularize code a lot, like below
# this will likely make LLM prompting easier
# also this demos default stroke or fill depending on type of mobject now being set with `color`
def smiley_face() -> VGroup:
    d1 = Dot(color=BLUE).shift(LEFT)
    d2 = Dot().shift(RIGHT)
    curve = Arc.from_points(d1.center, d2.center, angle=PI)
    curve.shift(DOWN).scale(0.8)
    d1.scale(0.6)
    d2.scale(0.6)
    return VGroup(d1, d2, curve)


def draw():
    upper = VGroup(smiley_face().shift(UR), smiley_face().shift(UL))
    b = Brace(upper, color=RED)
    canvas.add(b)
    canvas.add(upper)
    canvas.add(smiley_face().shift(DL))
    canvas.add(smiley_face().shift(DR))
    # canvas.draw()
    canvas.snapshot(preview=True)


draw()
