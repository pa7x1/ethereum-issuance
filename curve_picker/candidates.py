import numpy as np
import numpy.typing as npt
from typing import Union


def ethereum_issuance_yield(
    staked: Union[float, npt.NDArray[np.float64]],
) -> Union[float, npt.NDArray[np.float64]]:
    """
    Ethereum's current PoS issuance yield curve.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield coming from issuance.
    """
    return 1.0 + 2.6 * 64 * staked**-0.5


def ethereum_issuance_with_log_burn_yield(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve where a negative 'burn' term is introduced.
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (2.6 * 64 * (staked**-0.5) - b * np.log(1.0 + staked))


def ethereum_issuance_with_aggressive_log_burn_yield(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve where a negative 'burn' term is introduced.
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (2.6 * 64 * (staked**-0.5) - b * staked * np.log(1.0 + staked))


def quadratic_burn(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve with quadratic stake burn
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (2.6 * 64 * staked**-0.5 - b * staked**2.0)


def linear_burn(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve with quadratic stake burn
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (2.6 * 64 * staked**-0.5 - b * staked)

