# The Shape of Issuance Curves To Come: Part 2

## Staking Risk Premium and the Issuance Curve

The yield provided by staking Ethereum is market-driven, market participants expect to receive a premium for staking ETH vs. holding
ETH that compensates for the additional risks on which they partake. These risks are varied:

- Operational risks: Keeping the ETH or LST secure, smart contract risks, slashing risks...
- Liquidity risks: Staking ETH locks it in the staking contract, which makes it less liquid. LSTs alleviate some of that
illiquidity but may be subject to de-pegs, particularly when the exit and entry queues to the staking contract are full.
- Opportunity cost risks: Market opportunities you may not be able to take or would cause you to obtain worse yield if
you are staking instead of holding ETH.

The market weights all these risks and expects a yield to compensate for them. This yield is the result of the aggregate
behavior of holders and stakers, it's the yield at which the flow of holders becoming stakers and the flow of stakers
becoming holders balances out. Such that an equilibrium between both populations occurs. Borrowing terminology from A. Elowsson,
it's the _reservation yield of the marginal staker_.

Many of these risks will tend to decrease as time goes on, and this means that the risk premium will progressively get smaller and smaller.
To illustrate this, we will mention some ways in which the risks associated with staking have progressively gone down with time.

- Lindy effect: The probability of finding a new vulnerability on an existing smart contract keeps reducing
as its longevity increases. 
- Account security: Improved wallet UX, improved operational practices, advances in account abstraction, etc. make staking ETH less risky.
- Slashing protection: Slashing requires a very specific type of equivocation from the validator that can be entirely avoided with proper configuration
and awareness from the operator on which practices to avoid. Furthermore, slashing penalties have been reduced and clients offer some protections like [doppelganger protection](https://lighthouse-book.sigmaprime.io/validator_doppelganger.html). 
- Liquidity: LSTs mitigate to a large degree the liquidity risks of staking, even in situations where the entry and exit queues to the staking contract
are full, they have managed to maintain a reasonably good peg to their NAV. 
- Client diversity: Healthier client diversity has mitigated the risks of a single client bug resulting in large correlation penalties.
- Delta neutral strategies: Strategies that offer the yield of staking while hedging exposure with a short position on ETH
remove the risk of ETH price volatility while extracting the yield.
- Regulatory clarity: Completely external factors to the protocol like regulatory clarity, approval of staking ETFs,
can have a significant impact in reducing the risk premium of staking.

Overall, as the Ethereum network matures and the risks associated with staking are reduced, the risk premium demanded by market 
participants may continue to decrease.

The role of the issuance curve becomes clearer when the yield is seen for what it is, an independent variable set by the market.
The issuance curve does not control the yield stakers observe, which is set by the market. Its purpose is to match the yield demanded by the market,
given the risk premium, with a target stake rate. Such that the stake rate is not too low, which could lower economic security. 
And not too high, which could cause the protocol to overpay for security and push stakers to observe negative real yields at high stake rates.

### A General Argument for Stake Capping

It's impossible to know beforehand what will be the risk premium that the market will demand for staking. In particular,
as the risks of holding an LST keep reducing, this risk premium could get arbitrarily small. Therefore, the yield curve should 
be able to match a stake rate for any risk premium, however small it may be.

To make the case clearer, let's focus on the real yield curves (post dilution and costs) observed by different stakers 
from Ethereum's issuance, as currently implemented.

![Ethereum's Real Yield](./plots/ethereum_issuance/ethereum_real_yield_plot.png)

The dashed purple line represents the difference between the issuance real yield of holding an LST (green) vs. holding ETH (red).
This is the risk premium the market demands for an LST. If the risk premium of an LST were to drop below 1.5%, we could face ever-growing
stake rates. In this regime the issuance curve fails to match the risk premium with a target stake rate. We see 
this clearly if we flip the axis and treat the yield as the independent variable, which is what the market does.

![Risk Premium vs Stake Rate](plots/figures/inverse_function.png)

This function is not defined for small risk premiums. The yield curve fails to match any stake rate when the risk
premium gets low enough, roughly below 1.5%, which would cause runaway stake rates. If this were to happens, 
every staker would observe negative real yields, staking would become a cost for everyone.
Staking may be a losing proposition, but the holding yield is even worse which 
pushes ETH holders to convert to LST holders in the hopes of preventing further dilution. The end result of this regime
is bad for everyone; bad for stakers, bad for ETH holders, and bad for the decentralization of the network (as argued in the
previous post).

#### Formal Definition

We will denote the yield demanded by the market from staking as $y_s$ (yield of staking). The yield of staking ETH has two components, 
the issuance yield which is controlled by the protocol, $y_i$. And the exogenous yield, $y_e$ that results from all the economic activity 
built on top of the protocol and that provides a return to stakers (e.g., tips, MEV, restaking...).

Therefore, $y_s = y_i + y_e$.

**Assumption**: The yield associated with the risk premium of staking ETH, $y_s$, is an independent variable set by the market that
can get arbitrarily close to 0. $y_s \in [0, \infty)$.

**Assumption**: The exogenous yield may provide an additional, out of protocol, source of yield to stakers. Unless the
exogenous yield can be assumed to be capped, we assume $y_e \in [0, \infty)$.

As a consequence of these two general assumptions; the domain of the issuance yield must be $y_i \in (-\infty, \infty)$
so that for any risk premium, $y_s \in [0, \infty)$, and any exogenous yield, $y_e \in [0, \infty)$, the issuance curve 
can match the risk premium demanded by the market with a stake rate.

The inverse of the issuance yield curve $y_i^{-1}$ must be a continuous invertible function that maps the 
issuance yield set by the market ($y_i = y_s - y_e$) to a stake rate in the interval $(0, 1)$. 
That is, $y_i^{-1}: \mathbb{R} \to (0, 1)$.

We impose continuity such that small changes in the risk premium do not cause abrupt changes in the stake rate at which
this yield is met. That the function is invertible is necessary because its inverse is the yield curve that the 
protocol implements. In turn, the continuous and invertible conditions imply strict monotonicity. We can further constrain this monotonicity to
strictly decreasing monotonicity by noting that the issuance yield must go up when the stake rate goes to 0 
to ensure there is an economic incentive to attract stakers. The functions that satisfy these conditions are decreasing _sigmoid_ curves.

![Decreasing Sigmoid Functions](plots/figures/decreasing_sigmoid_family_handdrawn.png)

The yield curve ($y_i$) is the inverse of such a function. It's, therefore, a strictly decreasing function that maps the 
interval $(0, 1)$ to the real line. Like shown in the following figure:

![Issuance Yield Functions](plots/figures/issuance_yield_family_handdrawn.png)

As a direct application of the intermediate value theorem, there must be
a value for which the yield curve crosses 0. That is, the issuance curve implements stake capping.

#### Why are Negative Issuance Yields Needed?

To emphasize, the range of negative issuance yields is a direct consequence of the possible existence of exogenous yield.
If all sources of exogenous yield could be eliminated, then the issuance curve would inherit the same positive domain of
definition of the risk premium, $y_i \in [0, \infty)$. If exogenous yields can be assumed to be smaller than a certain bound, then
the issuance yield curve only needs to be negative up to that bound, $y_i \in [-y_e^{max}, \infty)$. But as long as exogenous yield exists, 
then the issuance curve must go negative to ensure the risk premium curve is well-defined and can always match a target 
stake rate for the given risk premium demanded by the market.

## How to Introduce Stake Capping on Ethereum

The analysis so far has been rather abstract and describes how, under general assumptions, the issuance curve needs
to adopt a specific form that implements stake capping. That is, provides 0 issuance yield at a certain target stake rate.  
And, in the presence of exogenous yield, must contain a regime of negative issuance yields 
to avoid certain pathological regimes that cause unbounded stake rate growth.

In this section we will go a step further and make a concrete proposal on how to implement a minimal change to the Ethereum
protocol to fix Ethereum's issuance curve and ensure it can match a healthy stake rate for any risk premium.

### Validator Duties and Economic Rewards

Ethereum's issuance fulfills a critical role in setting the economic incentives for a validator to perform its duties. A
validator gets paid through issuance for [attestations, sync committees, and block proposals](https://eth2book.info/capella/part2/incentives/rewards/).

If the rewards come from issuance and the issuance curve goes to 0 or even negative, does this mean that a validator
will be paid negative for meetings its duties? If that were the case, validators may start gaming the network to avoid
the cost associated with their duties, which would be very problematic.

Fortunately, this does not need to be the case! The trick is to leave the rewards associated with those duties as a positive
source of income for a validator and introduce a new negative term charged per epoch.

Concretely, the issuance curve needs to have 2 components in this approach. The issuance reward, $i_r$, is a positive term, 
and the issuance burn, $i_b$, implements the negative term:

$i(s) = R i_r(s) -  B i_b(s)$

By tweaking the analytic form of the 2 terms we can ensure that $i_b(s)$ overpowers $i_r(s)$ such that we can implement
stake capping.

By tweaking the ratio between the pre-factors of each term we can set the stake cap wherever we may need it. And by applying
a global factor to both we can set the desired yield at a particular stake rate. The following curve has been tweaked
to have the following properties:

- The reward term has the same analytic form as today, $i_r(s) \sim \sqrt{s}$.
- Stake Capping at 50M ETH, slightly before 50% stake rate.
- Yield at 25% stake rate fixed at 3%. Same as today's current curve at 25 %.

![Nominal Yield with Quadratic Burn](plots/quadratic_burn/ethereum_nominal_yield_with_quadratic_burn_plot.png)

### Healthy Stake Ranges

We have seen how we have full freedom to decide where should the stake cap be set. In this section we will provide a couple of
arguments that justify why the stake capping should be set before 50% stake rate. We will address this from two perspectives,
the first one is the point of view of the protocol. The second one is the point of view of a validator and their economic
self-interest.

**Protocol**

From the point of view of the protocol stake rates above 50% start to become problematic. Above these levels the majority 
of circulating supply is staking. In case of supermajority bug the majority of ETH holders could be incentivized to break
the consensus rules. The negative yield regime can be seen as a protection mechanism from the protocol to prevent 
this type of situations from happening. It sets an economic incentive to align the social layer with the protocol interests. 

**Validator**

From the point of view of a validator, stake rates above 50% start to be self-dilutive and get validators closer to the
point where they will observe negative real yields.

To make the case clear, let's focus on the two extremes; very low stake rates and very high stake rates.

At very low stake rates, the dilution effect of issuance is paid in full by holders which are the majority of the network.
At the other extreme, at stake rates close to 100%, the issuance income is completely coming from self-dilution. At those
levels staking yield is not real income, it's a redenomination of the unit of account. And when accounting for expenses
and taxes, pushes validators to observe negative real yields. Very high stake rates are bad for validators from a purely
economic perspective.

The point at which the transition between these 2 extremes happens is exactly at 50%. At stake rates beyond that point
most of the issuance income is self-dilution. Hence, the self-interest of a validator is to introduce stake capping before
50%.

### Target Yield

### Added Bonus

If we leave the reward term of the issuance curve untouched, the introduction of a negative term would diminish the 
yield provided. But in the example above we have tweaked the yield to lock it at 25% with the same yield provided with
today's issuance curve at 25%. This has an additional positive consequence; to achieve this result we must increase the
term $R$ with respect to today's curve. This means that the rewards coming from attestations, which represent the majority
of the regular steady income of a validator get increased with respect to the irregular sources of income (MEV, block proposals).

This curve would increase the steady source of income for a validator by 40% at 25% stake rate. This is good because irregular sources
of income tend to have centralizing effects.