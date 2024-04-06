from __future__ import annotations
from typing import Callable, Iterable, Sequence
import numpy as np

from smanim.mobject.geometry.polygon import Polygram
from smanim.mobject.graphing.scale import _ScaleBase, LinearBase
from smanim.mobject.vmobject import VGroup


class ParametricFunction(VGroup):
    """A parametric curve.

    Parameters
    ----------
    function
        The function to be plotted in the form of ``(lambda x: x**2)``
    t_range
        Determines the length that the function spans. By default ``[0, 1]``
    scaling
        Scaling class applied to the points of the function. Default of :class:`~.LinearBase`.
    use_smoothing
        Whether to interpolate between the points of the function after they have been created.
        (Will have odd behaviour with a low number of points)
    use_vectorized
        Whether to pass in the generated t value array to the function as ``[t_0, t_1, ...]``.
        Only use this if your function supports it. Output should be a numpy array
        of shape ``[[x_0, x_1, ...], [y_0, y_1, ...], [z_0, z_1, ...]]`` but ``z`` can
        also be 0 if the Axes is 2D
    discontinuities
        Values of t at which the function experiences discontinuity.
    dt
        The left and right tolerance for the discontinuities.

    .. attention::
        If your function has discontinuities, you'll have to specify the location
        of the discontinuities manually. See the following example for guidance.

    .. manim:: DiscontinuousExample
        :save_last_frame:

        class DiscontinuousExample(Scene):
            def construct(self):
                ax1 = NumberPlane((-3, 3), (-4, 4))
                ax2 = NumberPlane((-3, 3), (-4, 4))
                VGroup(ax1, ax2).arrange()
                discontinuous_function = lambda x: (x ** 2 - 2) / (x ** 2 - 4)
                incorrect = ax1.plot(discontinuous_function, color=RED)
                correct = ax2.plot(
                    discontinuous_function,
                    discontinuities=[-2, 2],  # discontinuous points
                    dt=0.1,  # left and right tolerance of discontinuity
                    color=GREEN,
                )
                self.add(ax1, ax2, incorrect, correct)
    """

    def __init__(
        self,
        function: Callable[
            [float, float], float
        ],  # domain is x values on cartesian graph and range are actual point values in the scene
        underlying_function: Callable[
            [float, float], float
        ],  # domain is x values on cartesian graph and range is y values on cartesian graph
        t_range: Sequence[float] | None = None,
        scaling: _ScaleBase = LinearBase(),
        dt: float = 1e-8,
        discontinuities: Iterable[float] | None = None,
        # use_smoothing: bool = True,
        use_vectorized: bool = False,
        **kwargs,
    ):
        self.function = function
        self.underlying_function = underlying_function
        t_range = [0, 1, 0.01] if t_range is None else t_range
        if len(t_range) == 2:
            t_range = np.array([*t_range, 0.01])

        self.scaling = scaling

        self.dt = dt
        self.discontinuities = discontinuities
        # self.use_smoothing = use_smoothing
        self.use_vectorized = use_vectorized
        self.t_min, self.t_max, self.t_step = t_range

        super().__init__(**kwargs)
        self.add_subcurves(default_stroke_color=self.stroke_color)

    def get_function(self):
        return self.function

    def get_point_from_function(self, t):
        return self.function(t)

    def add_subcurves(self, **polygram_style) -> None:
        if self.discontinuities is not None:
            discontinuities = filter(
                lambda t: self.t_min <= t <= self.t_max,
                self.discontinuities,
            )
            discontinuities = np.array(list(discontinuities))
            boundary_times = np.array(
                [
                    self.t_min,
                    self.t_max,
                    *(discontinuities - self.dt),
                    *(discontinuities + self.dt),
                ],
            )
            boundary_times.sort()
        else:
            boundary_times = [self.t_min, self.t_max]

        for t1, t2 in zip(boundary_times[0::2], boundary_times[1::2]):
            t_range = np.array(
                [
                    *self.scaling.function(np.arange(t1, t2, self.t_step)),
                    self.scaling.function(t2),
                ],
            )

            if self.use_vectorized:
                x, y, z = self.function(t_range)
                if not isinstance(z, np.ndarray):
                    z = np.zeros_like(x)
                points = np.stack([x, y, z], axis=1)
            else:
                points = np.array([self.function(t) for t in t_range])

            polygram = Polygram(points, **polygram_style)
            self.add(polygram)
            # make smooth used to be here and would be useful to have

    def gen_derivative_fn(
        self,
    ) -> Callable[[float, float], float]:
        x_max = self.t_max
        f = self.underlying_function
        discontinuities = self.discontinuities
        dt = self.dt

        prev_slope = 1

        def deriv(x, h=0.0001):
            nonlocal prev_slope
            if x + h > x_max:
                x = x - h
            if discontinuities is not None and any(
                np.isclose(disc, x, rtol=dt) for disc in discontinuities
            ):
                slope = prev_slope
            else:
                slope = (f(x + h) - f(x)) / h
                prev_slope = slope
            return slope

        return deriv
