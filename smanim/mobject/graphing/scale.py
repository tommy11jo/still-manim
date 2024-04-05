from __future__ import annotations

from typing import Iterable


__all__ = ["LinearBase"]


from smanim.mobject.mobject import Mobject


# Note: taken directly from manim community edition
class _ScaleBase:
    """Scale baseclass for graphing/functions.

    Parameters
    ----------
    custom_labels
        Whether to create custom labels when plotted on a :class:`~.NumberLine`.
    """

    def __init__(self, custom_labels: bool = False):
        self.custom_labels = custom_labels

    def function(self, value: float) -> float:
        """The function that will be used to scale the values.

        Parameters
        ----------
        value
            The number/``np.ndarray`` to be scaled.

        Returns
        -------
        float
            The value after it has undergone the scaling.

        Raises
        ------
        NotImplementedError
            Must be subclassed.
        """
        raise NotImplementedError

    def inverse_function(self, value: float) -> float:
        """The inverse of ``function``. Used for plotting on a particular axis.

        Raises
        ------
        NotImplementedError
            Must be subclassed.
        """
        raise NotImplementedError

    def get_custom_labels(
        self,
        val_range: Iterable[float],
    ) -> Iterable[Mobject]:
        """Custom instructions for generating labels along an axis.

        Parameters
        ----------
        val_range
            The position of labels. Also used for defining the content of the labels.

        Returns
        -------
        Dict
            A list consisting of the labels.
            Can be passed to :meth:`~.NumberLine.add_labels() along with ``val_range``.

        Raises
        ------
        NotImplementedError
            Can be subclassed, optional.
        """
        raise NotImplementedError


class LinearBase(_ScaleBase):
    def __init__(self, scale_factor: float = 1.0):
        """The default scaling class.

        Parameters
        ----------
        scale_factor
            The slope of the linear function, by default 1.0
        """

        super().__init__()
        self.scale_factor = scale_factor

    def function(self, value: float) -> float:
        """Multiplies the value by the scale factor.

        Parameters
        ----------
        value
            Value to be multiplied by the scale factor.
        """
        return self.scale_factor * value

    def inverse_function(self, value: float) -> float:
        """Inverse of function. Divides the value by the scale factor.

        Parameters
        ----------
        value
            value to be divided by the scale factor.
        """
        return value / self.scale_factor


# TODO: Add LogBase
