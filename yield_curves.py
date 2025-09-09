from typing import Union
import numpy as np
import numpy.typing as npt
from common import CIRCULATING_SUPPLY


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
    return 1. + (2.6 * 64 * (staked ** -0.5) - 2.6 * np.log(staked) / 2048.)

def ethereum_issuance_with_burn_2_yield(staked: Union[float, npt.NDArray[np.float64]]) -> Union[float, npt.NDArray[np.float64]]:
    """
    A variant of ethereum_issuance_with_burn_yield where the yield is simply x2.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1. + 2. * (2.6 * 64 * (staked ** -0.5) - 2.6 * np.log(staked) / 2048.)

def ethereum_issuance_with_burn_yield_adjusted(staked: Union[float, npt.NDArray[np.float64]]) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve where a negative 'burn' term is introduced.
    Parameters are adjusted to closely resemble a realistic proposal.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1. + 3.5 * (2.6 * 64 * (staked ** -0.5) - 2.6 * np.log(staked) / 2048.)

def tempered_issuance(staked: Union[float, npt.NDArray[np.float64]], k: int = 2**25) -> Union[float, npt.NDArray[np.float64]]:
    """
    Tempered issuance yield curve as proposed by A. Elowsson.
    :param staked: Amount of ETH staked.
    :param k: The k parameter that determines the stake at which yields peak.
    :return: The annualized nominal yield.
    """
    return 1. + 2.6 * 64 * staked ** -0.5 / (1 + staked / k)

def log_issuance_with_burn_yield(staked: Union[float, npt.NDArray[np.float64]]) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve where a negative 'burn' term is introduced targeting a max stake rate.

    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1. + 2.6 * (np.log(1. - (staked / CIRCULATING_SUPPLY)) - np.log(staked / CIRCULATING_SUPPLY)) / 128.

def vitaliks_issuance_yield(staked: Union[float, npt.NDArray[np.float64]]) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal by V. Buterin for Ethereum's issuance yield curve where a negative 'burn' term is introduced.
    Source: https://notes.ethereum.org/@vbuterin/single_slot_finality#Economic-capping-of-total-deposits
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1. + 2.6 * 64 * ((staked ** -0.5) - 0.5 * (2 ** 25 - staked) ** -0.5)