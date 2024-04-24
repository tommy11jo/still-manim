import inspect
from typing import List
import linecache

mobject_registry = {}

# PROOF OF CONCEPT FOR TRACING
# show I can obtain the top-level line number for any instance and generate code to access that instance


def register_instances(cls):
    original_init = cls.__init__

    def new_init(self: Mobject, *args, **kwargs):
        original_init(self, *args, **kwargs)
        caller_frame = inspect.currentframe().f_back
        upper_frame = caller_frame
        while hasattr(upper_frame, "f_back") and upper_frame.f_back is not None:
            upper_frame = upper_frame.f_back

        # upper_lineno = upper_frame.f_lineno if upper_frame != caller_frame else 0
        upper_lineno = upper_frame.f_lineno
        direct_lineno = caller_frame.f_lineno

        metadata = {
            "direct_lineno": direct_lineno,
            "upper_lineno": upper_lineno,
            "instance": self,
        }
        filename = caller_frame.f_code.co_filename
        line = linecache.getline(filename, upper_lineno).strip()
        if direct_lineno == upper_lineno:
            tokens = line.strip().split("=")
            if len(tokens) == 2:
                # only handles direct assignments
                self.subpath = tokens[0].strip()

        mobject_registry[id(self)] = metadata

    cls.__init__ = new_init
    return cls


class Mobject:
    def __init__(self, parent=None, subpath=None):
        self.parent: Mobject = parent
        self.subpath = subpath

    def get_path(self):
        path = self.parent.get_path() if self.parent else ""
        path += self.subpath if self.subpath else ""
        return path


@register_instances
class Square(Mobject):
    def __init__(self, side_length=1, **kwargs):
        super().__init__(**kwargs)
        self.side_length = side_length
        # for simplicity
        mobjects_to_draw.append(self)


@register_instances
class DoubleSquare(Mobject):
    def __init__(self, side_length=1, **kwargs):
        super().__init__(**kwargs)
        self.inner = Square(side_length, parent=self, subpath=".inner")
        self.outer = Square(side_length + 0.1, parent=self, subpath=".outer")
        mobjects_to_draw.append(self)


@register_instances
class NestedDoubleSquare(DoubleSquare):
    def __init__(self, side_length=1, **kwargs):
        super().__init__(**kwargs)
        self.inner = DoubleSquare(side_length, parent=self, subpath=".inner")
        self.outer = DoubleSquare(side_length + 0.1, parent=self, subpath=".outer")
        mobjects_to_draw.append(self)


mobjects_to_draw: List[Mobject] = []


def draw():
    for mobject in mobjects_to_draw:
        print(mobject.get_path())


# Contraints:
# - Cannot handle multiple assignment
# a = DoubleSquare()
b = NestedDoubleSquare()
print(mobject_registry)
draw()
