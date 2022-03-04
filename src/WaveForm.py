from scipy import signal
import numpy as np


class WaveForm:
    """Generate a Wave Form based on

    Args:
        amp (int): amplitude
        n (int): length of the array (n,)
        zero (int, optional): pre- and post zero periode. Defaults to 0, must be given in p.u.
    """

    def __init__(self, amp, n, zero=0) -> None:
        self._amp = amp
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
        saw = (
            (signal.sawtooth(2 * np.pi * np.linspace(0, 1, ramp), 0.5) + 1)
            / 2
            * self._amp
        )
        no_val_vec = np.zeros(shape=(no_val,))
        return np.append(np.append(no_val_vec, saw), no_val_vec)
