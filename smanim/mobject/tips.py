import numpy as np
from smanim.constants import DEFAULT_ARROW_TIP_LENGTH
from smanim.mobject.polygon import Triangle
from smanim.mobject.vmobject import VMobject
from smanim.typing import Point3D, Vector3D
from smanim.utils.color import WHITE


class ArrowTip(VMobject):
    """Base class for arrow tips."""

    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError("Has to be implemented in subclass")

    @property
    def base(self) -> Point3D:
        """The base point of the arrow tip. This is the point connecting to the arrow line."""
        raise NotImplementedError("Has to be implemented in subclass")
        # return self.point_from_proportion(0.5)

    @property
    def tip_point(self) -> Point3D:
        """The tip point of the arrow tip."""
        return self.points[0]

    @property
    def vector(self) -> Vector3D:
        """The vector pointing from the base point to the tip point."""
        return self.tip_point - self.base

    @property
    def tip_angle(self) -> float:
        """The angle of the arrow tip."""
        x, y = np.array(self.vector)[:2]
        return np.arctan2(y, x)

    @property
    def length(self) -> np.floating:
        """The length of the arrow tip."""
        return np.linalg.norm(self.vector)


class ArrowTriangleTip(ArrowTip, Triangle):
    """Triangular arrow tip."""

    def __init__(
        self,
        fill_opacity: float = 0.0,
        stroke_width: float = 3.0,
        length: float = DEFAULT_ARROW_TIP_LENGTH,
        width: float = DEFAULT_ARROW_TIP_LENGTH,
        **kwargs,
    ) -> None:
        Triangle.__init__(
            self,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            **kwargs,
        )

        self.stretch_to_fit_width(length)
        self.stretch_to_fit_height(width)

    @property
    def base(self):
        vertices = self.get_vertices()
        return (vertices[1] + vertices[2]) / 2


class ArrowTriangleFilledTip(ArrowTriangleTip):
    """Triangular arrow tip with filled tip."""

    def __init__(self, fill_opacity: float = 1.0, fill_color=WHITE, **kwargs) -> None:
        super().__init__(fill_opacity=fill_opacity, fill_color=fill_color, **kwargs)
