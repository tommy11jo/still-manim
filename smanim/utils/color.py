class ManimColor:
    value: str
    alpha: float = 1.0

    def __init__(self, value: str, alpha: float = 1.0):
        self.value = value
        self.alpha = alpha

    def __repr__(self):
        class_name = self.__class__.__qualname__
        return f"{class_name}(value={self.value}, alpha={self.alpha})"


# handles the case where "default_fill_color" is set first but then "default_stroke_color" is set later in the ancestor chain
# expected behavior is "default_fill_color" takes effect
def has_default_colors_set(**kwargs):
    return "default_stroke_color" in kwargs or "default_fill_color" in kwargs


WHITE = ManimColor("#FFFFFF")
BLACK = ManimColor("#000000")
BLUE = ManimColor("#58C4DD")
GREEN = ManimColor("#83C167")
YELLOW = ManimColor("#FFFF00")
RED = ManimColor("#FC6255")
PURPLE = ManimColor("#9A72AC")
PINK = ManimColor("#D147BD")
ORANGE = ManimColor("#FF862F")
