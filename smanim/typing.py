from typing import Hashable, List, Tuple, TypeAlias, Union
import numpy.typing as npt
import numpy as np


ManimFloat: TypeAlias = np.float64
ManimInt: TypeAlias = np.int64

# Point Types
PointDType: TypeAlias = ManimFloat

InternalPoint2D: TypeAlias = npt.NDArray[PointDType]
Point2D: TypeAlias = Union[InternalPoint2D, Tuple[float, float]]

PointDType: TypeAlias = ManimFloat
InternalPoint3D: TypeAlias = npt.NDArray[PointDType]
Point3D: TypeAlias = Union[InternalPoint3D, Tuple[float, float, float]]

InternalPoint3D_Array: TypeAlias = npt.NDArray[PointDType]
Point3D_Array: TypeAlias = Union[
    InternalPoint3D_Array, Tuple[Tuple[float, float, float], ...]
]

QuadArray_Point3D: TypeAlias = List[Tuple[Point3D, Point3D, Point3D, Point3D]]

# Vector Types
Vector3: TypeAlias = npt.NDArray[PointDType]

# Graph Types
AdjacencyListGraph: TypeAlias = dict[Hashable, List[Tuple[Hashable, Hashable]]]
WeightedAdjacencyListGraph = dict[Hashable, List[Tuple[Hashable, Hashable, Hashable]]]
