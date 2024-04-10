from typing_extensions import Self
from smanim.constants import (
    DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
    DOWN,
    LEFT,
    ORIGIN,
    OUT,
    PI,
    RIGHT,
    UP,
)
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

    def arrange_in_grid(
        self,
        rows: int | None = None,
        cols: int | None = None,
        row_aligned_edge: Vector3 = UP,
        col_aligned_edge: Vector3 = LEFT,
        row_direction: Vector3 = RIGHT,
        col_direction: Vector3 = DOWN,
        buff_within_row: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
        buff_within_col: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
    ):
        # Assumes items are of uniform width
        all_children = self.get_family()[1:]
        num_items = len(all_children)

        if rows is not None and cols is not None:
            if num_items != rows * cols:
                raise ValueError(
                    "rows * cols must equal number of arranged items, when both vars are specified"
                )
        elif cols is not None:
            rows = (num_items + cols - 1) // cols  # Calculate rows needed for all items
        elif rows is not None:
            cols = (
                num_items + rows - 1
            ) // rows  # Calculate columns if rows are specified

        if rows is None or cols is None:
            raise ValueError("Either rows or cols must be specified.")

        row_groups = Group()
        for i in range(rows):
            row_group = Group(*all_children[i * cols : (i + 1) * cols])
            row_group.arrange(
                direction=row_direction,
                aligned_edge=row_aligned_edge,
                buff=buff_within_row,
            )
            row_groups.add(row_group)
        row_groups.arrange(
            direction=col_direction, aligned_edge=col_aligned_edge, buff=buff_within_col
        )
