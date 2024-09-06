from typing import Union
import numpy as np
import numpy.typing as npt


def ethereum_issuance_yield(staked: Union[float, npt.NDArray[np.float64]]) -> Union[float, npt.NDArray[np.float64]]:
    """
    Ethereum's current PoS issuance yield curve.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield coming from issuance.
    """
    return 1. + 2.6 * 64 * staked ** -0.5

def ethereum_issuance_with_burn_yield(staked: Union[float, npt.NDArray[np.float64]]) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve where a negative 'burn' term is introduced.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1. + 2.6 * 64 * (staked ** -0.5) - 2.6 * np.log(staked) / 2048.

def ethereum_issuance_with_burn_2_yield(staked: Union[float, npt.NDArray[np.float64]]) -> Union[float, npt.NDArray[np.float64]]:
    """
    A variant of ethereum_issuance_with_burn_yield where the yield is simply x2.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1. + 2.6 * 128 * (staked ** -0.5) - 2.6 * np.log(staked) / 1024.
