from pathlib import Path
from smanim.canvas import Canvas
from smanim.config import Config
from smanim import *


config = Config(save_file_dir=Path(__file__).parent / "media")
canvas = Canvas(config=config)


def simpleNumberLine():
    n = NumberLine([-3, 4, 1])
    canvas.add(n)
    canvas.snapshot(preview=True)


# simpleNumberLine()


# TODO: fix line cap awkwardness on ends of arrows
# Number line with vector on particular points and with start and end arrows
def numberLineWithVector():

    # n = NumberLine([-3, 4, 1], start_tip=ArrowTriangleFilledTip())
    start_arrow = Arrow(start=LEFT / 2, end=RIGHT / 2)
    end_arrow = Arrow(start=LEFT / 2, end=RIGHT / 2)
    n = NumberLine([-3, 4, 1], start_tip_arrow=start_arrow, end_tip_arrow=end_arrow)
    v = Arrow(n.number_to_point(-2), n.number_to_point(2), fill_color=RED)
    g = Group(n, v)
    g.scale(1.5)
    canvas.add(g)
    canvas.snapshot(preview=True)


numberLineWithVector()
