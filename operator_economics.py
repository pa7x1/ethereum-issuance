"""
Economics of professional node operators.

Operators stake other people's ETH for a fee, so the real-yield framing used for
staker archetypes does not apply to them: their business is fee revenue against
fixed USD costs. The quantity of interest is the break-even delegation — the
minimum ETH under operation needed to cover costs — and how it moves with the
issuance policy.

Because operator revenue is a fraction of gross rewards, issuance curves that
taper yield towards 0 (or negative) squeeze operators too: as issuance vanishes
their revenue base collapses to the fee on EL rewards alone, and the break-even
delegation grows without bound. This is a consolidation force on the operator
market that a per-staker analysis does not surface.
"""

from typing import Union
import numpy as np
from numpy import typing as npt

from cost_models import NodeOperatorModel, ETH_PRICE_USD, el_reward_yield


def operator_annual_profit_usd(operator: NodeOperatorModel,
                               delegated_eth: float,
                               staked: Union[float, npt.NDArray[np.float64]],
                               issuance_yield: Union[float, npt.NDArray[np.float64]],
                               eth_price_usd: float = ETH_PRICE_USD) -> Union[float, npt.NDArray[np.float64]]:
    """
    Annual operator profit in USD.
    :param operator: The operator's cost model.
    :param delegated_eth: ETH delegated to (staked through) this operator.
    :param staked: Total ETH staked network-wide (sets the EL reward yield).
    :param issuance_yield: The nominal issuance yield at that stake level.
    :param eth_price_usd: ETH price used to convert fee revenue to USD.
    :return: Annual profit in USD.
    """
    gross_reward_yield = np.maximum(0., (issuance_yield - 1.) + el_reward_yield(staked))
    revenue = operator.fee_on_rewards * gross_reward_yield * delegated_eth * eth_price_usd
    return revenue - operator.annual_fixed_usd


def module_program_breakeven_tvl_eth(program_cost_usd: float,
                                     program_reward_share: float,
                                     staked: Union[float, npt.NDArray[np.float64]],
                                     issuance_yield: Union[float, npt.NDArray[np.float64]],
                                     eth_price_usd: float = ETH_PRICE_USD) -> Union[float, npt.NDArray[np.float64]]:
    """
    Minimum module TVL for a staking-module program (CSM, Rocket Pool) to cover
    its sponsor's program costs from its share of the module's gross rewards.
    :param program_cost_usd: Annual program overhead (development, audits,
    oracles, support) in USD.
    :param program_reward_share: The sponsor's share of the module's gross
    staking rewards available to fund the program.
    :param staked: Total ETH staked network-wide (sets the EL reward yield).
    :param issuance_yield: The nominal issuance yield at that stake level.
    :param eth_price_usd: ETH price used to convert reward revenue to USD.
    :return: Break-even module TVL in ETH (inf where gross rewards are <= 0).
    """
    gross_reward_yield = (issuance_yield - 1.) + el_reward_yield(staked)
    revenue_per_eth = program_reward_share * gross_reward_yield * eth_price_usd
    return np.where(revenue_per_eth > 0., program_cost_usd / np.maximum(revenue_per_eth, 1e-30), np.inf)


def operator_breakeven_delegation_eth(operator: NodeOperatorModel,
                                      staked: Union[float, npt.NDArray[np.float64]],
                                      issuance_yield: Union[float, npt.NDArray[np.float64]],
                                      eth_price_usd: float = ETH_PRICE_USD) -> Union[float, npt.NDArray[np.float64]]:
    """
    Minimum delegated ETH for the operator to cover its fixed costs.
    :param operator: The operator's cost model.
    :param staked: Total ETH staked network-wide (sets the EL reward yield).
    :param issuance_yield: The nominal issuance yield at that stake level.
    :param eth_price_usd: ETH price used to convert fee revenue to USD.
    :return: Break-even delegation in ETH (inf where gross rewards are <= 0).
    """
    gross_reward_yield = (issuance_yield - 1.) + el_reward_yield(staked)
    revenue_per_eth = operator.fee_on_rewards * gross_reward_yield * eth_price_usd
    return np.where(revenue_per_eth > 0., operator.annual_fixed_usd / np.maximum(revenue_per_eth, 1e-30), np.inf)
