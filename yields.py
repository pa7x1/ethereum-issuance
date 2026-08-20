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


def real_staking_yield(issuance_yield: Union[float, npt.NDArray[np.float64]],
                       supply: float,
                       staked: Union[float, npt.NDArray[np.float64]],
                       fixed_cost_ratio: float,
                       reward_fee: float,
                       tax_rate: float,
                       exogenous_yield: Union[float, npt.NDArray[np.float64]] = 0.0,
                       anticorrelation_incentives: float = 0.0) -> Union[float, npt.NDArray[np.float64]]:
    """
    The yield observed by stakers net of costs and circulating supply changes, with the cost
    structure decomposed into fixed costs, fees on rewards, and taxes, and with support for
    exogenous (execution-layer) rewards.

    Differences with `real_issuance_yield`:

    - Fees and taxes are applied in order (fees on gross rewards, taxes on post-fee rewards)
    instead of as a single blended scaling factor, so archetypes that pay both can be modeled
    accurately.

    - Exogenous rewards (priority fees + MEV) add to the staker's rewards but are recycled ETH,
    not new supply, so they are excluded from the dilution denominator. For the same reason
    anticorrelation incentives (a redistribution between validators) do not alter total dilution.

    :param issuance_yield: The nominal issuance yield.
    :param supply: The circulating supply.
    :param staked: Amount of token staked.
    :param fixed_cost_ratio: Costs that do not scale with yield (HW, internet, labor...)
    expressed as a ratio of the amount staked.
    :param reward_fee: Fraction of gross rewards paid as fees (e.g. LST or operator fees).
    :param tax_rate: Tax rate applied to post-fee rewards.
    :param exogenous_yield: Additive yield from execution-layer rewards (priority fees + MEV),
    already scaled by the staker's MEV capture.
    :param anticorrelation_incentives: Nominal yield changes due to uncorrelation incentives
    introduced in the protocol.
    :return: The real yield experienced by stakers.
    """
    gross_rewards = (issuance_yield - 1.) + anticorrelation_incentives + exogenous_yield
    post_fee_rewards = gross_rewards - np.maximum(0., reward_fee * gross_rewards)
    net_rewards = post_fee_rewards - np.maximum(0., tax_rate * post_fee_rewards)
    real_yield = (1. - fixed_cost_ratio + net_rewards) \
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