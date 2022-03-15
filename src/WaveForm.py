from scipy import signal
import math
import numpy as np


class WaveForm:
    """Generate a Wave Form based on

    Args:
        amp (int): amplitude
        n (int): length of the array (n,)
        zero (int, optional): pre- and post zero periode. Defaults to 0, must be given in p.u.
    """

    def __init__(self, amp, n, zero=0, offset=0) -> None:
        self._amp = amp
        if abs(offset) < amp * 0.5:
            self._offset = offset
        else:
            self._offset = 0
        self.N = n
        if zero > 1 or zero < 0:
            raise ValueError(
                "Zero periode  in {} cannot exeed 100% or be negative. (zero = {}%)".format(
                    self.__class__.__name__, zero * 100
                )
            )

        self._zero = zero

    def triangle(self):
        """Returns a triangular (single-peak) wave with pre and post zero field.

        Returns:
            [np.linspace]: field-vector
        """
        no_val = int(self._zero * self.N)
        ramp = self.N - 2 * no_val

        if self._offset != 0:
            return self.__triag_offset(no_val, ramp)

        saw = (
            (signal.sawtooth(2 * np.pi * np.linspace(0, 1, ramp), 0.5) + 1)
            / 2
            * self._amp
        )
        no_val_vec = np.zeros(shape=(no_val,))
        return np.append(np.append(no_val_vec, saw), no_val_vec)

    def __triag_offset(self, no_val, ramp):
        """Ugly array stitching to enable field offset."""
        baseline = np.ones(shape=(no_val,)) * self._offset
        rup = np.linspace(self._offset, self._amp, int(ramp / 2))
        return np.append(np.append(np.append(baseline, rup), np.flip(rup)), baseline)

    @staticmethod
    def linear(start, stop, step):
        """Returns a linear spaced vector from start to stop with spacing step.
        If the range (stop - start) is greater than the step size but does not fit an even number of values spaced by step, it will fit range/step steps in the range.
        Args:
                start (int): start point
                stop (int): stop point
                step (int): spacing
        Returns:
                [np.linspace]: linear vector"""
        d_tmp = abs(stop - start)
        if step > (d_tmp) or step < 0:
            raise ValueError("Step size too large or smaller than 0.")

        n = math.ceil(d_tmp / step) + 1
        return np.linspace(start, stop, n)
