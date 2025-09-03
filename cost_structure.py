# Fixed costs represent the ratio between costs that don't scale with size of stake (annualized) and amount of staked.
# For home staking is the cost of HW, energy, internet... divided total value staked.
## E.g. 1000 USD of HW (over 5 years ~ 200 USD/year),
## 100 USD per year on electricity for a typical NUC
## home internet not included because it's already paid by personal use
## 300 USD per year / (4500 USD/ETH x 32 ETH) ~ 0.002
# For an LST it's essentially 0 because all costs scale with total amount staked
# For institutional is very close to 0 due to their sheer scale

# Scaling costs represent the costs that scale with the size of the stake
# For home staking is basically income tax.
# For an LST is capital gains tax.
# For institutional is corporate income tax + the lofty management salaries that they pay themselves.

# Details may vary between jurisdictions, update these values with your own.
# The figures below are estimates that should be roughly representative of each stakeholder


home_staking = {'fixed_costs': 2. / 1000.,
                'scaling_costs': 0.35}

lst_staking = {'fixed_costs': 0.,
               'scaling_costs': 0.10}

institutional_staking = {'fixed_costs': 0.,
                         'scaling_costs': 0.25}
