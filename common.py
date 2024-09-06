from typing import Union
import numpy as np
import numpy.typing as npt

CIRCULATING_SUPPLY = 120_000_000


def percentage_yield(m_yield: Union[float, npt.NDArray[np.float64]]) -> Union[float, npt.NDArray[np.float64]]:
    return 100. * (m_yield - 1.)
