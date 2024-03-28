class ManimColor:
    value: str
    alpha: float = 1.0

    def __init__(self, value: str, alpha: float = 1.0):
        self.value = value
        self.alpha = alpha

    def __repr__(self):
        class_name = self.__class__.__qualname__
        return f"{class_name}(value={self.value}, alpha={self.alpha})"


WHITE = ManimColor("#FFFFFF")
BLACK = ManimColor("#000000")
BLUE = ManimColor("#58C4DD")
GREEN = ManimColor("#83C167")
YELLOW = ManimColor("#FFFF00")
RED = ManimColor("#FC6255")
PURPLE = ManimColor("#9A72AC")
PINK = ManimColor("#D147BD")
ORANGE = ManimColor("#FF862F")
