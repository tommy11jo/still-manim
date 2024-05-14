import math
from typing_extensions import Self
from smanim.constants import (
    DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
)
from smanim.mobject.mobject import Mobject
from smanim.mobject.transformable import TransformableMobject
from smanim.typing import Point2D, Point3D, Vector3
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
            m2.next_to(m1, direction=direction, buff=buff).align_to(
                m1, edge=aligned_edge
            )
        if center:
            self.move_to_origin()
        return self

    def arrange_in_grid(
        self,
        num_rows: int | None = None,
        num_cols: int | None = None,
        aligned_edge_within_row: Vector3 = UP,
        aligned_edge_within_col: Vector3 = LEFT,
        row_direction: Vector3 = RIGHT,
        col_direction: Vector3 = DOWN,
        buff_within_row: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
        buff_within_col: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
        buff: float | None = None,  # overrides row and col buff
    ) -> Self:
        if buff is not None:
            buff_within_row = buff
            buff_within_col = buff

        # Assumes items are of uniform width
        all_children = self.get_family()[1:]
        num_items = len(all_children)
        if num_rows is not None and num_cols is not None:
            if num_items != num_rows * num_cols:
                raise ValueError(
                    "rows * cols must equal number of arranged items, when both vars are specified"
                )
        elif num_cols is not None:
            num_rows = (num_items + num_cols - 1) // num_cols
        elif num_rows is not None:
            num_cols = (num_items + num_rows - 1) // num_rows
        else:
            num_rows = math.ceil(math.sqrt(num_items))
            num_cols = num_items // num_rows

        row_groups = Group()
        for i in range(num_rows):
            row_group = Group(*all_children[i * num_cols : (i + 1) * num_cols])
            row_group.arrange(
                direction=row_direction,
                aligned_edge=aligned_edge_within_row,
                buff=buff_within_row,
            )
            row_groups.add(row_group)
        row_groups.arrange(
            direction=col_direction,
            aligned_edge=aligned_edge_within_col,
            buff=buff_within_col,
        )
        return self

    def get_closest_intersecting_point_2d(
        self, ray_origin: Point2D, ray_direction: Point2D
    ) -> Point3D:
        """Unlike Mobject's function of this name that uses bounding points, this function uses bbox."""
        return self.get_closest_intersecting_point_2d_helper(
            self.bbox, ray_origin, ray_direction
        )
