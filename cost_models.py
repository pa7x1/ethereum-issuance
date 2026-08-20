"""
Structured cost models for the different staking archetypes.

This module refines the scalar probes in `cost_structure.py` (kept untouched for
comparison) in three ways:

1. Costs are built bottom-up from USD line items (hardware amortization, power,
   internet, labor at an hourly rate) instead of being collapsed a priori into a
   single ratio. This makes each assumption individually auditable and tunable.

2. Execution-layer rewards (priority fees + MEV) are modeled as an exogenous
   yield term. The total EL reward pie is roughly independent of the issuance
   policy, so as issuance comes down (or stake grows) EL rewards automatically
   become a larger share of gross rewards. EL rewards are recycled ETH, not new
   supply, so they must NOT enter the dilution denominator.

3. EL rewards are unevenly distributed: block-level MEV is heavy-tailed, so the
   median proposer reward sits well below the mean. Large operators and pools
   smooth over many proposals and realize the mean; a solo staker with ~2-3
   proposals per year typically realizes something closer to the median. We
   model this with a `mev_capture` factor (expected value is the same for all,
   but the typical realized outcome — what drives churn — is not).

Default figures are taken from https://validatorcosts.kyne.eu (which pulls live
data from CoinGecko and Beaconcha.in). As with `cost_structure.py`, these are
representative 'probes'; update them to reflect your own situation.
"""

from dataclasses import dataclass
import numpy as np


# Base case uses roughly today's market price; USD-fixed costs against
# ETH-denominated stakes make every viability figure price-sensitive, so the
# analysis also reports an appreciation scenario. An expectation of
# appreciation lets a staker tolerate temporary negative real yield (their
# future cost ratio shrinks), so the base-case crossings are floors on
# rational exit, not triggers.
ETH_PRICE_USD = 2500.
ETH_PRICE_APPRECIATED_USD = 4000.

# Labor: validatorcosts.kyne.eu default time value. The original cost_structure
# valued hobbyist time at 0; ongoing maintenance is real work (updates, disk
# pruning, client bugs, missed-attestation triage) and pricing it at 0 hides a
# structural advantage of delegation.
HOURLY_RATE_USD = 20.

# Hardware straight-line depreciation. validatorcosts.kyne.eu uses 4 years;
# the original cost_structure.py used 5. See `home_staker_annual_fixed_usd`
# to evaluate the sensitivity.
HARDWARE_LIFESPAN_YEARS = 4.

# Taxes on staking rewards for individuals. The original probe used the ~20%
# OECD average marginal rate on labor income, but staking rewards in most
# western jurisdictions are taxed as ordinary/capital income in the 25-30%
# range (US: ordinary income 22-37% federal; UK: 20/40/45%; DE: personal rate;
# FR: 30% flat PFU; ES: 19-28% savings income). 30% is a representative probe.
# Rebasing LSTs can defer realization to sale; treat that as a sensitivity.
STAKING_INCOME_TAX = 0.30

# Execution-layer rewards (priority fees + MEV), total annual pie in ETH.
# Calibrated so EL yield is ~0.35% at today's ~34M ETH staked, consistent with
# beaconcha.in showing ~3% gross APR vs ~2.8% issuance-only. This pie is set by
# blockspace demand, not by the issuance policy.
EL_REWARDS_ANNUAL_ETH = 120_000.

# Median-vs-mean EL capture. Proposer EL rewards are heavy-tailed (median
# block well below the mean due to rare outsized-MEV blocks). Pools and large
# operators propose thousands of blocks and realize the mean (1.0); a typical
# solo staker's realized capture over a hardware lifespan is closer to the
# median. 0.5 is a probe for the median/mean ratio.
SOLO_MEV_CAPTURE = 0.5
POOLED_MEV_CAPTURE = 1.0


@dataclass(frozen=True)
class StakerCostModel:
    """
    Cost structure of a staker archetype.

    :param stake_eth: Size of the stake in ETH, used to convert USD fixed costs
    into a ratio of the stake.
    :param annual_fixed_usd: Annualized USD costs that do not scale with the
    stake or the yield (hardware amortization, power, internet, labor).
    :param reward_fee: Fraction of gross rewards paid as fees (LST/operator fee).
    :param tax_rate: Tax rate applied to post-fee rewards.
    :param mev_capture: Share of the average EL reward yield actually realized.
    """
    stake_eth: float
    annual_fixed_usd: float
    reward_fee: float
    tax_rate: float
    mev_capture: float

    def fixed_cost_ratio(self, eth_price_usd: float = ETH_PRICE_USD) -> float:
        """Annual fixed USD costs as a fraction of the USD value of the stake."""
        return self.annual_fixed_usd / (self.stake_eth * eth_price_usd)


def el_reward_yield(staked: float) -> float:
    """
    Average execution-layer (priority fees + MEV) yield at a given stake level.
    The total EL pie is fixed in ETH terms, so per-ETH yield falls as stake
    grows and is unaffected by the issuance policy.
    :param staked: Amount of ETH staked.
    :return: Annualized EL reward yield (additive, e.g. 0.0035 for 0.35%).
    """
    return EL_REWARDS_ANNUAL_ETH / staked


"""
Home Staker Assumptions (validatorcosts.kyne.eu defaults):
- HW: 1000 USD (incl. spares), straight-line over 4 years -> 250 USD/year
- Electricity: 30 W continuous at 0.18 USD/kWh -> ~47 USD/year
- Internet: 10 USD/month allocation of the home bill -> 120 USD/year.
  Not zeroed: staking measurably degrades a shared home connection, and this
  is a commonly reported reason for home-staker churn. A partial allocation
  of the bill is the honest accounting.
- Labor: 0.5 h/month maintenance at 20 USD/h -> 120 USD/year,
  plus 4 h setup amortized over the hardware lifespan -> 20 USD/year
- Total: ~557 USD/year (~0.44% of a 32 ETH stake at 4000 USD/ETH; the original
  probe was 300 USD/year ~ 0.23%)
- Taxed as income on gross rewards; realizes ~median EL rewards (heavy tail).
"""

HOME_HW_COST_USD = 1000.
HOME_POWER_WATTS = 30.
HOME_ELECTRICITY_USD_PER_KWH = 0.18
HOME_INTERNET_MONTHLY_USD = 10.
HOME_MAINTENANCE_HOURS_PER_MONTH = 0.5
HOME_SETUP_HOURS = 4.


def home_staker_annual_fixed_usd(hardware_lifespan_years: float = HARDWARE_LIFESPAN_YEARS) -> float:
    """Bottom-up annual fixed costs of a home staker, parameterized on hardware lifespan."""
    hardware = HOME_HW_COST_USD / hardware_lifespan_years
    electricity = HOME_POWER_WATTS * 24. * 365. / 1000. * HOME_ELECTRICITY_USD_PER_KWH
    internet = HOME_INTERNET_MONTHLY_USD * 12.
    labor = HOME_MAINTENANCE_HOURS_PER_MONTH * 12. * HOURLY_RATE_USD
    setup = HOME_SETUP_HOURS * HOURLY_RATE_USD / hardware_lifespan_years
    return hardware + electricity + internet + labor + setup


home_staker = StakerCostModel(
    stake_eth=32.,
    annual_fixed_usd=home_staker_annual_fixed_usd(),
    reward_fee=0.,
    tax_rate=STAKING_INCOME_TAX,
    mev_capture=SOLO_MEV_CAPTURE,
)

"""
Retail Delegator Assumptions (~1k ETH or less, via an LST or exchange):
- Fixed costs: negligible (an ERC-20 swap), rounded to 0.
- Fee: ~10% of rewards at retail (Lido 10%, Rocket Pool 14%, exchanges 15-25%).
- Taxed at the same individual rate; rebasing LSTs may defer to sale (treat as
  a sensitivity, not the base case).
- EL rewards are smoothed across the pool -> mean capture.
"""

retail_delegator = StakerCostModel(
    stake_eth=1_000.,
    annual_fixed_usd=0.,
    reward_fee=0.10,
    tax_rate=STAKING_INCOME_TAX,
    mev_capture=POOLED_MEV_CAPTURE,
)

"""
Whale Delegator Assumptions (~100k ETH, negotiated institutional delegation):
- Fixed costs: negligible relative to stake, rounded to 0.
- Fee: ~1% of rewards at this size (retail 10% compresses to ~1% at 100k ETH;
  the spread between this and the ~0.5-3% the node operator receives is taken
  by custodians/LST wrappers, not modeled yet).
- EL rewards smoothed -> mean capture.

This archetype replaces the previous 'institutional staking' probe (5% of
rewards in salaries + 21% US corporate tax). Enterprises self-staking their
own treasury are rare; the economically relevant large player is a holder who
delegates at negotiated fees.
"""

whale_delegator = StakerCostModel(
    stake_eth=100_000.,
    annual_fixed_usd=0.,
    reward_fee=0.01,
    tax_rate=STAKING_INCOME_TAX,
    mev_capture=POOLED_MEV_CAPTURE,
)


"""
Matched Home Operator Assumptions (bonded small operators running validators
funded largely by other people's ETH):

- Lido CSM (https://lido.fi/csm): bond of 2.4 ETH for the first validator and
  1.3 ETH per subsequent one, held as stETH (so it rebases at the delegator
  rate, net of the ~10% protocol fee). The operator additionally receives a
  reward share of each full 32 ETH validator's rewards: 3.5% on the default
  permissionless track, 6% on the first 16 keys for the vetted Identified
  Community Staker (ICS) tier. Validators are funded entirely from the pool,
  so the commission base is the full 32 ETH per validator.

- Rocket Pool LEB8 (https://docs.rocketpool.net/upgrades/atlas/lebs): the
  operator bonds 8 ETH inside the validator, borrows 24 ETH from the pool,
  earns full rewards on the own 8 ETH plus a 14% commission on the borrowed
  24 ETH's rewards. RPL collateral (min ~10% of borrowed value) is required
  on top and is not modeled here -- it makes the economics somewhat worse.

In both cases the operator earns a levered, commission-like return on own
capital -- a transfer from delegators, not just issuance. Same hardware/labor
budget as the solo staker; EL rewards are smoothed by the protocols, so mean
MEV capture. The commission floors at 0 if validator rewards go negative (no
fee is paid on losses), while the bond bears its own share of any burn.
"""

CSM_BOND_FIRST_ETH = 2.4
CSM_BOND_NEXT_ETH = 1.3
CSM_PERMISSIONLESS_REWARD_SHARE = 0.035
CSM_ICS_REWARD_SHARE = 0.06
LIDO_PROTOCOL_FEE = 0.10
VALIDATOR_SIZE_ETH = 32.

ROCKETPOOL_LEB8_BOND_ETH = 8.
ROCKETPOOL_LEB8_BORROWED_ETH = 24.
ROCKETPOOL_COMMISSION = 0.14


@dataclass(frozen=True)
class MatchedOperatorModel:
    """
    A bonded home operator running validators matched against pool ETH.

    :param label: Human-readable name used in tables and plots.
    :param bond_eth: The operator's own capital at risk.
    :param commission_base_eth: The ETH balance whose rewards the commission
    applies to (full validator size for CSM, borrowed ETH for Rocket Pool).
    :param commission: Fraction of the base's rewards paid to the operator.
    :param bond_fee: Protocol fee applied to the bond's own staking rewards
    (Lido fee on the stETH bond; 0 for a Rocket Pool bond staked directly).
    :param annual_fixed_usd: Annualized USD operating costs (same rig as a solo).
    :param tax_rate: Tax on the operator's net rewards.
    """
    label: str
    bond_eth: float
    commission_base_eth: float
    commission: float
    bond_fee: float
    annual_fixed_usd: float
    tax_rate: float = STAKING_INCOME_TAX

    def gross_yield_on_bond(self, reward_rate):
        """
        Gross yield on the operator's own capital given the per-ETH staking reward
        rate (issuance net of any burn, plus smoothed EL rewards). The bond earns
        its own (fee-adjusted) rewards; the commission is levered by the base over
        the bond and floors at 0 when rewards go negative.
        """
        bond_rewards = reward_rate - np.maximum(0., self.bond_fee * reward_rate)
        commission_rewards = np.maximum(0., self.commission * reward_rate) \
            * self.commission_base_eth / self.bond_eth
        return bond_rewards + commission_rewards


def _csm_bond(n_validators: int) -> float:
    return CSM_BOND_FIRST_ETH + CSM_BOND_NEXT_ETH * (n_validators - 1)


csm_single = MatchedOperatorModel(
    label="CSM permissionless (1 validator, 2.4 ETH bond)",
    bond_eth=_csm_bond(1),
    commission_base_eth=VALIDATOR_SIZE_ETH,
    commission=CSM_PERMISSIONLESS_REWARD_SHARE,
    bond_fee=LIDO_PROTOCOL_FEE,
    annual_fixed_usd=home_staker.annual_fixed_usd,
)

csm_ten = MatchedOperatorModel(
    label="CSM permissionless (10 validators, 14.1 ETH bond)",
    bond_eth=_csm_bond(10),
    commission_base_eth=10 * VALIDATOR_SIZE_ETH,
    commission=CSM_PERMISSIONLESS_REWARD_SHARE,
    bond_fee=LIDO_PROTOCOL_FEE,
    annual_fixed_usd=home_staker.annual_fixed_usd,
)

csm_ics_ten = MatchedOperatorModel(
    label="CSM ICS (10 validators, 6% share)",
    bond_eth=_csm_bond(10),
    commission_base_eth=10 * VALIDATOR_SIZE_ETH,
    commission=CSM_ICS_REWARD_SHARE,
    bond_fee=LIDO_PROTOCOL_FEE,
    annual_fixed_usd=home_staker.annual_fixed_usd,
)

rocketpool_ten = MatchedOperatorModel(
    label="Rocket Pool LEB8 (10 minipools, 80 ETH bond)",
    bond_eth=10 * ROCKETPOOL_LEB8_BOND_ETH,
    commission_base_eth=10 * ROCKETPOOL_LEB8_BORROWED_ETH,
    commission=ROCKETPOOL_COMMISSION,
    bond_fee=0.,
    annual_fixed_usd=home_staker.annual_fixed_usd,
)

"""
Industrial Self-Staker Assumptions (kept as a minor cohort; treasury companies
and exchanges staking their own ETH at scale are rare relative to delegation):
- 100k ETH of own stake on professional infrastructure (~12.6k USD/yr, the
  node-operator rig below), no fees, US corporate tax, smoothed EL rewards.
"""

industrial_self_staker = StakerCostModel(
    stake_eth=100_000.,
    annual_fixed_usd=12_640.,
    reward_fee=0.,
    tax_rate=0.21,
    mev_capture=POOLED_MEV_CAPTURE,
)


"""
Staking Module Program Assumptions:
- CSM and Rocket Pool are not just operator economics; they are products that
  a sponsor organization must build and run: protocol development, audits,
  oracles, monitoring, support, governance. That program overhead plausibly
  runs into millions of USD per year for each core team.
- The program's native funding is the sponsor's share of the module's gross
  staking rewards (for Lido, the treasury's part of the 10% fee after the
  operator share; Rocket Pool funds development differently, via RPL, but the
  economic requirement is equivalent). If that share of module rewards cannot
  cover the program, the rail exists only by cross-subsidy -- and issuance
  curves that taper rewards shrink the sponsor's whole revenue base at once.
- Reference module sizes (~mid-2026): CSM ~770k ETH, Rocket Pool ~530k ETH.
"""

MODULE_PROGRAM_COST_USD = 3_000_000.
MODULE_PROGRAM_REWARD_SHARE = 0.04
CSM_MODULE_SIZE_ETH = 770_000.
ROCKETPOOL_MODULE_SIZE_ETH = 530_000.


@dataclass(frozen=True)
class NodeOperatorModel:
    """
    A professional node operator staking other people's ETH for a fee.
    Unlike the staker archetypes, the operator's economics are a fee business:
    revenue = fee x gross rewards on delegated stake, against fixed USD costs.

    :param annual_fixed_usd: Annualized USD operating costs.
    :param fee_on_rewards: Fraction of gross staking rewards kept as the
    operator fee (0.5%-3% typical; the delegator-side fee is higher because
    custodians/LST wrappers take the spread).
    """
    annual_fixed_usd: float
    fee_on_rewards: float


"""
Node Operator Assumptions:
- HW/hosting: 5 servers in a datacenter at 200 USD/month -> 12,000 USD/year.
  Genuinely fixed with respect to delegated stake (up to capacity), unlike the
  previous probe's 5%-of-rewards salary term.
- Labor: 1 h/month at 40 USD/h (twice the home staker's hours and rate)
  -> 480 USD/year, plus 16 h setup amortized over 4 years -> 160 USD/year.
- Total: ~12,640 USD/year.
"""

OPERATOR_SERVERS = 5.
OPERATOR_SERVER_MONTHLY_USD = 200.
OPERATOR_HOURLY_RATE_USD = 2. * HOURLY_RATE_USD
OPERATOR_MAINTENANCE_HOURS_PER_MONTH = 2. * HOME_MAINTENANCE_HOURS_PER_MONTH
OPERATOR_SETUP_HOURS = HOME_SETUP_HOURS + 12.

operator_annual_fixed_usd = (
    OPERATOR_SERVERS * OPERATOR_SERVER_MONTHLY_USD * 12.
    + OPERATOR_MAINTENANCE_HOURS_PER_MONTH * 12. * OPERATOR_HOURLY_RATE_USD
    + OPERATOR_SETUP_HOURS * OPERATOR_HOURLY_RATE_USD / HARDWARE_LIFESPAN_YEARS
)

node_operator_budget = NodeOperatorModel(annual_fixed_usd=operator_annual_fixed_usd, fee_on_rewards=0.005)
node_operator_mid = NodeOperatorModel(annual_fixed_usd=operator_annual_fixed_usd, fee_on_rewards=0.01)
node_operator_premium = NodeOperatorModel(annual_fixed_usd=operator_annual_fixed_usd, fee_on_rewards=0.03)
