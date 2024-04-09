from typing_extensions import Self
from smanim.constants import DEFAULT_MOBJECT_TO_MOBJECT_BUFFER, ORIGIN, OUT, PI, RIGHT
from smanim.mobject.mobject import Mobject
from smanim.mobject.transformable import TransformableMobject
from smanim.typing import Point3D, Vector3
from smanim.utils.color import ManimColor

__all__ = ["Group"]


class Group(TransformableMobject):
    def __init__(self, *mobjects, **kwargs):
        super().__init__(**kwargs)
        self.add(*mobjects)

    def __repr__(self) -> str:
        return f'{self.__class__.__qualname__}({", ".join(str(mob) for mob in self.submobjects)})'

    def __iter__(self):
        return iter(self.submobjects)

    def __getitem__(self, index: int) -> Mobject:
        return self.submobjects[index]

    def __len__(self):
        return len(self.submobjects)

    def __add__(self, mobject: Mobject) -> Self:
        return Group(*self.submobjects, mobject)

    def __iadd__(self, mobject: Mobject) -> Self:
        return self.add(mobject)

    def add(self, *mobjects: Mobject, insert_at_front: bool = False) -> Self:
        return super().add(*mobjects, insert_at_front=insert_at_front)

    def rotate(
        self,
        angle: float = PI / 4,
        axis: Vector3 = OUT,
        about_point: Point3D | None = ORIGIN,
    ) -> Self:
        for mob in self.submobjects:
            mob.rotate(angle, axis, about_point)
        return self

    def scale(self, factor: float, about_point: Point3D = ORIGIN) -> Self:
        for mob in self.submobjects:
            mob.scale(factor, about_point)
        return self

    def stretch(self, factor: float, dim: int) -> Self:
        for mob in self.submobjects:
            mob.stretch(factor, dim)
        return self

    def shift(self, vector: Vector3) -> Self:
        for mob in self.submobjects:
            mob.shift(vector)
        return self

    def set_color(self, color: ManimColor, family: bool = True) -> Self:
        for mob in self.submobjects:
            mob.set_color(color, family=True)
        return self

    def set_opacity(self, opacity: float, family: bool = True) -> Self:
        for mob in self.submobjects:
            mob.set_opacity(opacity, family=True)
        return self

    def arrange(
        self,
        direction: Vector3 = RIGHT,
        aligned_edge: Vector3 = ORIGIN,
        buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
        center: bool = True,
    ) -> Self:
        for m1, m2 in zip(self.submobjects, self.submobjects[1:]):
            m2.next_to(m1, direction=direction, aligned_edge=aligned_edge, buff=buff)
        if center:
            self.center()
        return self


# TODO: arrange in grid
