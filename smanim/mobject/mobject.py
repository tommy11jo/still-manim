from __future__ import annotations


from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum
from typing import List, NamedTuple, Sequence, Tuple, Type
from typing_extensions import Self

import numpy as np

from smanim.config import CONFIG
from smanim.constants import (
    DEFAULT_MOBJECT_TO_EDGE_BUFFER,
    DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
    DL,
    DOWN,
    DR,
    LEFT,
    ORIGIN,
    RIGHT,
    UL,
    UP,
    UR,
)
from smanim.typing import (
    InternalPoint3D_Array,
    Point2D,
    Point3D,
    Point3D_Array,
    Vector3,
)
from smanim.utils.color import ManimColor
from smanim.utils.logger import log
from smanim.utils.space_ops import line_intersect, polygon_intersection

__all__ = ["Mobject"]


class AccessType(Enum):
    TOP_LEVEL_ASSIGN = "top-level-assign"
    MANUAL_ASSIGN = "manual-assign"
    ADD_TO_GROUP = "add-to-group"
    ADD_TO_CANVAS = "add-to-canvas"


class AccessPath(NamedTuple):
    type: AccessType
    subpath: str | None = None
    parent: Mobject | None = None
    lineno: int | None = None  # only set on top-level assignments
    mob_id: int | None = None  # only set by group additions
    # mob_id is used to generate index at retrieval using `parent._index_of_submobject(mob_id)`


class Mobject(ABC):
    """Base class for all objects that take up space.
    Note: This class has been modified to support bidirectional editing.
    `bounding_points` represents the bounding polygon for this mobject (they do not include submobjects).
    Subclasses are responsible for setting the `bounding_points`.
    """

    def __init__(
        self,
        bounding_points: InternalPoint3D_Array | None = None,
        z_index: int = 0,
        parent: Mobject | None = None,
        subpath: str | None = None,
        lineno: int | None = None,
    ):
        if bounding_points is None:
            bounding_points = np.empty((0, 3))
        self._bounding_points = bounding_points
        self.z_index = z_index
        self.submobjects: List[Mobject] = []

        # used for bidirectional editing
        self.access_paths: List[AccessPath] = []
        if subpath:
            first_path = AccessPath(
                type=AccessType.MANUAL_ASSIGN,
                subpath=subpath,
                parent=parent,
                lineno=lineno,
            )
            self.access_paths.append(first_path)

    @property
    def bounding_points(self):
        return self._bounding_points

    @bounding_points.setter
    def bounding_points(self, bounding_points: InternalPoint3D_Array):
        self._bounding_points = bounding_points

    def get_access_path(self) -> Tuple[str | None, int | None]:
        """Return the first valid access path and its corresponding lineno"""
        access_type_precedence = {
            AccessType.TOP_LEVEL_ASSIGN: 0,
            AccessType.MANUAL_ASSIGN: 1,
            AccessType.ADD_TO_GROUP: 2,
            AccessType.ADD_TO_CANVAS: 3,
        }

        # Implictly, this also guarantees earlier access paths take precedence over later ones
        sorted_access_paths = sorted(
            self.access_paths,
            key=lambda ap: access_type_precedence[ap.type],
        )

        for access_path in sorted_access_paths:
            access_type, subpath, parent, lineno, mob_id = access_path
            if access_type == AccessType.TOP_LEVEL_ASSIGN:
                return subpath, lineno
            elif access_type == AccessType.MANUAL_ASSIGN:
                if not parent:
                    return subpath, lineno
                parent_path, parent_lineno = parent.get_access_path()
                path = parent_path + subpath if parent_path is not None else subpath
                lineno = parent_lineno if lineno is None else lineno
                return path, lineno
            elif access_type == AccessType.ADD_TO_GROUP:
                parent_path, parent_lineno = parent.get_access_path()
                if not mob_id:
                    raise AttributeError(
                        f"Add to group paths must have a mobject id. Mobject is {self}"
                    )
                if parent_path is None:
                    # Invalid path, should be skipped
                    continue

                # Generate subpath dynamically for mobjects in groups by finding their index
                index = parent._index_of_submobject(mob_id)
                subpath = f"[{index}]"
                if lineno is None:
                    lineno = parent_lineno
                return parent_path + subpath, lineno
            elif access_type == AccessType.ADD_TO_CANVAS:
                return subpath, lineno
            else:
                raise TypeError("Invalid access type")
        return None, None

    # Grouping
    def add(self, *mobjects: Mobject, insert_at_front: bool = False) -> Self:
        new_mobjects = []
        for mobject in mobjects:
            if mobject is self:
                raise ValueError("Cannot add mobject to itself")
            if mobject in self.submobjects:
                log.warning(f"Mobject already added: {mobject}")
            else:
                new_mobjects.append(mobject)
                new_access_path = AccessPath(
                    type=AccessType.ADD_TO_GROUP,
                    parent=self,
                    mob_id=id(mobject),
                )
                mobject.access_paths.append(new_access_path)
        if not insert_at_front:
            self.submobjects.extend(new_mobjects)
        else:
            self.submobjects = new_mobjects + self.submobjects
        return self

    def _index_of_submobject(self, sub_mob_id: str):
        for index, sub_mob in enumerate(self.submobjects):
            if id(sub_mob) == sub_mob_id:
                return index
        return -1

    def remove(self, *mobjects: Mobject) -> Self:
        for mobject in mobjects:
            if mobject is self:
                log.error("Cannot remove mobject from itself")
            if mobject not in self.submobjects:
                log.warning(f"Mobject not found: {mobject}")
            else:
                self.submobjects.remove(mobject)
        return self

    def get_family(self):
        family = [self]
        for s in self.submobjects:
            family.extend(s.get_family())
        return family

    def get_family_members_of_type(self, member_type: Type):
        cur_family = [self] if isinstance(self, member_type) else []
        for s in self.submobjects:
            cur_family.extend(s.get_family_members_of_type(member_type))
        return cur_family

    # Bounding Box Ops
    def get_critical_point(self, direction: Vector3):
        """9 point bbox: 4 corners, 4 edge points, 1 center"""
        direction = direction.astype(int)
        if not (-1 <= direction[0] <= 1 and -1 <= direction[1] <= 1):
            raise ValueError(
                f"Direction is {direction} but must be [x, x, (optional)] where x is -1, 0, 1. See constants.py for direction values."
            )

        all_points = np.concatenate(
            [mob.bounding_points for mob in self.get_family()], axis=0
        )

        x_min, y_min, _ = np.min(all_points, axis=0)
        x_max, y_max, _ = np.max(all_points, axis=0)
        x_mid, y_mid = x_min + (x_max - x_min) / 2, y_min + (y_max - y_min) / 2
        # bbox_dirs = [UL, UP, UR, RIGHT, DR, DOWN, DL, LEFT, ORIGIN]
        x_dir = [x_min, x_mid, x_max]
        y_dir = [y_min, y_mid, y_max]

        new_x = x_dir[direction[0] + 1]
        new_y = y_dir[direction[1] + 1]

        return np.array([new_x, new_y, 0])

    # Rule: All positional attrs that can be a property should be
    @property
    def top(self):
        return self.get_critical_point(UP)

    @property
    def bottom(self):
        return self.get_critical_point(DOWN)

    @property
    def left(self):
        return self.get_critical_point(LEFT)

    @property
    def right(self):
        return self.get_critical_point(RIGHT)

    @property
    def center(self):
        return self.get_critical_point(ORIGIN)

    def get_corner(self, direction: Vector3):
        if not any(np.array_equal(direction, cdir) for cdir in [UL, UR, DR, DL]):
            raise ValueError("`direction` must be a corner")
        return self.get_critical_point(direction)

    @property
    def bbox(self) -> Point3D_Array:
        return [self.get_corner(dir) for dir in [UR, UL, DL, DR]]

    @property
    def width(self):
        return (self.right - self.left)[0]

    @property
    def height(self):
        return (self.top - self.bottom)[1]

    def get_closest_intersecting_point_2d(
        self, ray_origin: Point2D, ray_direction: Point2D
    ) -> Point3D:
        """Return the closest intersecting point between a ray and the bounding polygon of this mobject.
        Handles rays shot from within or from outside the bounding polygon.
        """
        return self.get_closest_intersecting_point_2d_helper(
            self.bounding_points, ray_origin, ray_direction
        )

    def get_closest_intersecting_point_2d_helper(
        self,
        bounding_points: Point3D_Array,
        ray_origin: Point2D,
        ray_direction: Point2D,
    ) -> Point3D:
        points_ahead = np.roll(bounding_points, -1, axis=0)
        line_segments = [(p1, p2) for p1, p2 in zip(bounding_points, points_ahead)]
        intersections_and_params = []
        for p1, p2 in line_segments:
            intersection, param = line_intersect(
                ray_origin, ray_direction, p1[:2], p2[:2]
            )
            intersections_and_params.append(
                (intersection, param) if intersection is not None else (None, np.inf)
            )
        intersection, param = min(intersections_and_params, key=lambda x: x[1])
        if intersection is None:
            log.warning("No intersection point found. Illegal ray input.")
            return self.center
        return np.array([intersection[0], intersection[1], 0])

    # Absolute Positioning
    def set_position(self, coord: Point2D | Point3D) -> Self:
        """Set the center of this mobject to `coord`."""
        if len(coord) == 2:
            coord = np.append(coord, 0)
        return self.shift(coord - self.center)

    def set_x(self, x: float) -> Self:
        """Set x value of the center of this mobject"""
        x_pt = self.center.copy()
        x_pt[0] = x
        return self.set_position(x_pt)

    def set_y(self, y: float) -> Self:
        """Set y value of the center of this mobject"""
        y_pt = self.center.copy()
        y_pt[1] = y
        return self.set_position(y_pt)

    # Relative Positioning, using core transformations
    def next_to(
        self,
        mobject_or_point: Mobject | Point3D,
        direction: Vector3 = RIGHT,  # think of this as bbox point
        aligned_edge: Vector3 | None = None,
        buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
    ) -> Self:
        """Moves this mobject to the edge of another mobject, given by `direction`. Optionally aligns the edges perpendicular to `direction` using `aligned_edge`."""
        self._require_direction_as_bbox(direction)

        if isinstance(mobject_or_point, Mobject):
            dest_pt = mobject_or_point.get_critical_point(direction)
        else:
            dest_pt = mobject_or_point

        cur_pt = self.get_critical_point(-direction)
        to_shift = (dest_pt - cur_pt) + direction * buff
        self.shift(to_shift)

        if aligned_edge is not None:
            self.align_to(mobject_or_point, aligned_edge)
        return self

    def close_to(
        self,
        mobject_or_point: Mobject,
        obstacle_mobjects: Sequence[Mobject],  # potentially colliding mobjects
        direction: Vector3 = RIGHT,  # the direction to try first
        buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
    ) -> Self:
        """Moves this mobject close to another mobject, like `next_to`.
        Except that other directions are tried if the specified `direction` causes an intersection.
        Is only an approximation since it treats the `bounding_points` as a polygon rather than bezier curves.
        A faster approach could use bboxes but would be less precise.
        """
        if not isinstance(mobject_or_point, Mobject):
            raise TypeError("Only mobjects are handled")

        # Try these directions in order and accept the first one that does not cause an intersection
        directions = [direction, RIGHT, UP, LEFT, DOWN, UR, UL, DL, DR, direction]

        for dir in directions:
            self.next_to(mobject_or_point, dir, buff=buff)
            cur_bounding_points = self.bounding_points
            intersection_found = False
            for other in obstacle_mobjects:
                other_bounding_points = other.bounding_points
                if (
                    other is not self
                    and len(other_bounding_points) > 0
                    and polygon_intersection(cur_bounding_points, other_bounding_points)
                ):
                    intersection_found = True
                    break
            if not intersection_found:
                break
        return self

    def move_to(self, point_or_mobject: Point3D | Mobject) -> Self:
        """Moves the center of this mobject to the center of another mobject"""
        if isinstance(point_or_mobject, Mobject):
            dest_pt = point_or_mobject.get_critical_point(ORIGIN)
        else:
            dest_pt = point_or_mobject
        cur_pt = self.get_critical_point(ORIGIN)
        self.shift(dest_pt - cur_pt)

        return self

    def align_to(
        self,
        point_or_mobject: Point3D | Mobject,
        edge: Vector3 = UP,
        buff: float = 0,
    ) -> Self:
        """Align to the edge of another mobject"""
        if not any([np.array_equal(edge, e) for e in (UP, DOWN, LEFT, RIGHT, ORIGIN)]):
            raise ValueError("Edge must be one of (UP, DOWN, LEFT, RIGHT, ORIGIN)")
        if isinstance(point_or_mobject, Mobject):
            dest_pt = point_or_mobject.get_critical_point(edge)
        else:
            dest_pt = point_or_mobject
        cur = self.get_critical_point(edge)
        if np.array_equal(edge, UP) or np.array_equal(edge, DOWN):
            self.shift(np.array([0, dest_pt[1] - cur[1], 0]) - edge * buff)
        if np.array_equal(edge, LEFT) or np.array_equal(edge, RIGHT):
            self.shift(np.array([dest_pt[0] - cur[0], 0, 0]) - edge * buff)
        return self

    # TODO: Change this to move_to(ORIGIN)
    def move_to_origin(self) -> Self:
        self.shift(-self.center)
        return self

    def to_edge(
        self, edge: Vector3 = LEFT, buff: float = DEFAULT_MOBJECT_TO_EDGE_BUFFER
    ) -> Self:
        if not any([np.array_equal(edge, e) for e in (UP, DOWN, LEFT, RIGHT)]):
            raise ValueError("Edge must be one of (UP, DOWN, LEFT, RIGHT)")
        frame_x_radius = CONFIG.fw / 2
        frame_y_radius = CONFIG.fh / 2
        new_point = edge * np.array([frame_x_radius, frame_y_radius, 0])
        return self.align_to(new_point, edge, buff)

    # Core transformations must be overridden by all subclasses
    @abstractmethod
    def rotate(self, angle: float, axis: Vector3, about_point: Point3D) -> Self:
        raise NotImplementedError(
            "Use TransformableMobject to accept default spatial transformations."
        )

    @abstractmethod
    def scale(self, factor: float, about_point: Point3D) -> Self:
        raise NotImplementedError(
            "Use TransformableMobject to accept default spatial transformations."
        )

    @abstractmethod
    def stretch(self, factor: float, dim: int) -> Self:
        raise NotImplementedError(
            "Use TransformableMobject to accept default spatial transformations."
        )

    @abstractmethod
    def shift(self, vector: Vector3) -> Self:
        raise NotImplementedError(
            "Use TransformableMobject to accept default spatial transformations."
        )

    ## Layering
    # Rule: All else being equal, mobjects are painted in the order they are listed
    def bring_to_back(self, mobject: Mobject) -> Self:
        """Places a mobject behind all other mobjects within this mobject's family.
        Note: Use `bring_to_back` in canvas.py to place a mobject behind ALL other mobjects.
        """
        members = self.get_family()
        if mobject not in members:
            raise ValueError(
                "Mobject to be brought back must be in this mobject's family"
            )
        bottom_z_index = min([mob.z_index for mob in self.get_family()])
        if mobject.z_index == bottom_z_index:
            self.remove(mobject)
            self.add(mobject, insert_at_front=True)
        else:
            mobject.z_index = bottom_z_index - 1

        return self

    def bring_to_front(self, mobject: Mobject) -> Self:
        """Places a mobject in front of all other mobjects within this mobject's family.
        Note: Use `bring_to_front` in canvas.py to place a mobject in front of ALL other mobjects.
        """
        members = self.get_family()
        if mobject not in members:
            raise ValueError(
                "Mobject to be brought to front must be in this mobject's family"
            )
        top_z_index = max([mob.z_index for mob in self.get_family()])
        if mobject.z_index == top_z_index:
            self.remove(mobject)
            self.add(mobject)
        else:
            mobject.z_index = top_z_index + 1
        return self

    def set_z_index(self, value: int, family: bool = True) -> Self:
        for mob in self.get_family():
            mob.z_index = value
        return self

    # Style matching helpers
    def set_color(self, color: ManimColor, family: bool = False) -> Self:
        # Should be overriden in subclasses typically
        pass

    def set_opacity(self, opacity: float, family: bool = False) -> Self:
        # Should be overriden in subclasses typically
        pass

    # Frequently used patterns
    def copy(self) -> Mobject:
        return deepcopy(self)

    def _require_direction_as_bbox(self, direction: Vector3):
        if not any(
            [
                np.array_equal(direction, e)
                for e in (UP, DOWN, LEFT, RIGHT, UR, UL, DL, DR)
            ]
        ):
            raise ValueError("`direction` must be a bbox point, such as UP or LEFT")

    def __getitem__(self, index: int) -> Mobject:
        return self.submobjects[index]
