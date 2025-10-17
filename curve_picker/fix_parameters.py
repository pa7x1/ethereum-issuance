import math
from typing import Callable, Dict, Tuple
from common import CIRCULATING_SUPPLY
import curve_picker.candidates as c


def fix_parameters(
    yield_curve: Callable,
    stake_cap_ratio: float = 0.5,
    yield_target: Tuple[float, float] = (0.25, 1.03),
) -> Dict[str, float]:
    """
    Fixes the parameters k and b of a yield curve so that it implements the stake cap at the target stake ratio and provides the target yield at the desired stake ratio.
    """

    def curve_minus_one(b: float, staked: float) -> float:
        return yield_curve(1.0, b, staked) - 1.0

    def find_b() -> float:
        """Solve curve_minus_one(b, stake_cap_ratio) == 0 via bisection."""
        f_low = curve_minus_one(0.0, stake_cap_ratio)
        if f_low <= 0.0:
            raise ValueError(
                "Positive term of the curve must exceed the negative term when b = 0."
            )

        b_low = 0.0
        b_high = 1.0
        f_high = curve_minus_one(b_high, stake_cap_ratio * CIRCULATING_SUPPLY)

        # Expand the upper bound until the root is bracketed.
        max_iterations = 100
        expansion_count = 0
        while f_high > 0.0 and expansion_count < max_iterations:
            b_high *= 2.0
            f_high = curve_minus_one(b_high, stake_cap_ratio * CIRCULATING_SUPPLY)
            expansion_count += 1

        if f_high > 0.0:
            raise RuntimeError(
                "Failed to bracket root while searching for burn parameter b."
            )

        # Standard bisection loop.
        for _ in range(max_iterations):
            b_mid = 0.5 * (b_low + b_high)
            f_mid = curve_minus_one(b_mid, stake_cap_ratio * CIRCULATING_SUPPLY)
            if abs(f_mid) < 1e-9:
                return b_mid
            if f_mid > 0.0:
                b_low = b_mid
            else:
                b_high = b_mid

        return 0.5 * (b_low + b_high)

    b_value = find_b()

    target_staked, target_yield = yield_target
    curve_margin = curve_minus_one(b_value, target_staked * CIRCULATING_SUPPLY)
    if math.isclose(curve_margin, 0.0, abs_tol=1e-12):
        raise ValueError("Cannot determine k because the curve margin is zero.")

    k_value = (target_yield - 1.0) / curve_margin

    return {"k": k_value, "b": b_value}
