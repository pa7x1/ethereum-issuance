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


def eip8363_tapered_burn(
    staked: Union[float, npt.NDArray[np.float64]],
    saturation_balance: float = 60_250_000.,
) -> Union[float, npt.NDArray[np.float64]]:
    """
    The tapered issuance burn proposed in EIP-8363 (ethereum/EIPs#12081), permanent
    (post-transition) state with BASE_REWARD_FACTOR 64. Each validator's issuance is
    reduced by a burn fraction b = (D / SATURATION_BALANCE)^(3/2), clamped to 1, which
    makes the net yield taper linearly in the staking ratio and reach 0 at the
    saturation balance (~50% of supply). The yield is floored at 0 and never negative,
    so this is a 'baguette'-type curve in this repo's taxonomy.
    :param staked: Amount of ETH staked.
    :param saturation_balance: Total active balance at which the burn reaches 100%.
    :return: The annualized nominal yield.
    """
    burn_fraction = np.minimum(1.0, (staked / saturation_balance) ** 1.5)
    return 1.0 + 2.6 * 64 * (staked**-0.5) * (1.0 - burn_fraction)


def log_burn(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve where a negative 'burn' term is introduced that scales as log s.
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (2.6 * 64 * (staked**-0.5) - b * np.log(1.0 + staked))


def log_burn_baguette(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve where a negative 'burn' term is introduced that scales as log s.
    Negative yields are capped at 0.
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (
        2.6 * 64 * (staked**-0.5)
        - np.minimum(2.6 * 64 * (staked**-0.5), b * np.log(1.0 + staked))
    )


def aggressive_log_burn(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve with a stake burn that scales as s * log s.
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (2.6 * 64 * (staked**-0.5) - b * staked * np.log(1.0 + staked))


def aggressive_log_burn_baguette(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve with a stake burn that scales as s * log s.
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (
        2.6 * 64 * (staked**-0.5)
        - np.minimum(2.6 * 64 * (staked**-0.5), b * staked * np.log(1.0 + staked))
    )


def quadratic_burn(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve with quadratic stake burn.
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (2.6 * 64 * staked**-0.5 - b * staked**2.0)

def quadratic_burn_baguette(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve with quadratic stake burn.
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (2.6 * 64 * staked**-0.5 - np.minimum(2.6 * 64 * staked**-0.5, b * staked**2.0))


def linear_burn(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve with a linear stake burn.
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (2.6 * 64 * staked**-0.5 - b * staked)

def linear_burn_baguette(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve with a linear stake burn.
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (
        2.6 * 64 * staked**-0.5 - np.minimum(b * staked, 2.6 * 64 * staked**-0.5)
    )

def constant_burn(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve where a constant negative 'burn' term is introduced.
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (2.6 * 64 * staked**-0.5 - b)

def constant_burn_baguette(
    k: float, b: float, staked: Union[float, npt.NDArray[np.float64]]
) -> Union[float, npt.NDArray[np.float64]]:
    """
    A proposal for Ethereum's issuance yield curve where a constant negative 'burn' term is introduced.
    :param k: A global yield multiplying factor.
    :param b: A pre-factor to weight the burn.
    :param staked: Amount of ETH staked.
    :return: The annualized nominal yield.
    """
    return 1.0 + k * (2.6 * 64 * staked**-0.5 - np.minimum(2.6 * 64 * staked**-0.5, b))