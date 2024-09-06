import numpy as np
import numpy.typing as npt
from typing import Union, Callable


def issuance(yield_curve: Callable[[Union[float, npt.NDArray[np.float64]]], Union[float, npt.NDArray[np.float64]]],
             staked: Union[float, npt.NDArray[np.float64]]) -> Union[float, npt.NDArray[np.float64]]:
    """
    How much token is issued given a yield curve and amount staked.
    :param yield_curve: A callable that returns the yield as a function of amount staked.
    :param staked: How much token is staked.
    :return: How much token is issued.
    """
    return staked * (yield_curve(staked) - 1.)
