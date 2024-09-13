from typing import Union
import numpy as np
from numpy import typing as npt


def effective_issuance_yield(issuance_yield: float,
                             supply: float,
                             staked: Union[float, npt.NDArray[np.float64]]) -> Union[float, npt.NDArray[np.float64]]:
    """
    The issuance yield observed by stakers net of circulating supply changes.
    :param issuance_yield: The nominal issuance yield.
    :param supply: The circulating supply.
    :param staked: Amount of token staked.
    :return: The effective yield experienced from issuance by stakers.
    """
    effective_yield = issuance_yield / (staked * (issuance_yield - 1.) / supply + 1.)
    return effective_yield


def real_issuance_yield(issuance_yield: float,
                        supply: float,
                        staked: Union[float, npt.NDArray[np.float64]],
                        fixed_costs: float,
                        scaling_costs: float,
                        anticorrelation_incentives: float = 0.0) -> Union[float, npt.NDArray[np.float64]]:
    """
    The issuance yield observed by stakers net of costs and circulating supply changes.
    :param issuance_yield: The nominal issuance yield.
    :param supply: The circulating supply.
    :param staked: Amount of token staked.
    :param fixed_costs: Costs that do not scale with yield (e.g. HW, internet, labor...) expressed as a ratio of the
    amount staked.
    :param scaling_costs: Costs that scale with the nominal yield (e.g. taxes, staking fees...).
    :param anticorrelation_incentives: Nominal yield changes due to uncorrelation incentives introduced in the protocol.
    :return: The real yield experienced from issuance by stakers.
    """
    issuance_yield = issuance_yield + anticorrelation_incentives
    real_yield = (1. - fixed_costs + (issuance_yield - 1.) - np.maximum(0., scaling_costs * (issuance_yield - 1.)))\
                 / (staked * (issuance_yield - 1.) / supply + 1.)
    return real_yield


def effective_holding_yield(issuance_yield: float,
                            supply: float,
                            staked: Union[float, npt.NDArray[np.float64]]) -> Union[float, np.ndarray]:
    """
    The issuance yield observed by non-staking holders net of circulating supply changes.
    :param issuance_yield: The nominal issuance yield.
    :param supply: The circulating supply.
    :param staked: Amount of token staked.
    :return: The effective yield experienced from issuance by holders.
    """
    effective_yield = 1. / (staked * (issuance_yield - 1.) / supply + 1.)
    return effective_yield