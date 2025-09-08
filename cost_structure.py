"""
- Fixed costs represent the ratio between costs that don't scale with size of stake (annualized) and amount staked.

- Scaling costs represent the costs that scale with the size of the stake

- Details may vary between jurisdictions. The below figures should be representative 'probes', if you are
interested in your own real yield, update these values with your own.
"""


"""
Home Staking Assumptions:
- Fixed Costs:
    - For home staking this is the cost of HW, energy, internet... divided by total value staked.
    - HW: Intel NUC or equivalent (4 TiB SSD, 16 GiB RAM), 1000 USD of HW (over 5 years ~ 200 USD/year),
    - Electricity: 100 USD per year on electricity for a typical NUC
    - Home internet not included, assumed paid by personal use
    - 300 USD per year / (4500 USD/ETH x 32 ETH) ~ 0.002
- Scaling Costs:
    - Average Marginal Income Tax (varies by country):
        - We want to know at which price 1 extra $ of income is taxed, this is the marginal income tax rate
        - We want a representative figure, the OECD marginal income tax rate average sits around 18%, we will round it to ~20%
        - Sources:
            - https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/04/taxing-wages-2024_f869da31/dbcbac85-en.pdf
            - https://data-explorer.oecd.org/vis?lc=en&df[ds]=dsDisseminateFinalDMZ&df[id]=DSD_TAX_PIT%40DF_PIT_MR&df[ag]=OECD.CTP.TPS&df[vs]=1.0&dq=.A....S13%2BS1311%2BS13M.S.S_C0....&lom=LASTNPERIODS&lo=1&to[TIME_PERIOD]=false&vw=ov
"""

HOME_VALIDATOR_SIZE = 32
ETH_PRICE_USD = 4000

HOME_HW_COSTS = 1000
HOME_ELECTRICITY_ANNUAL_COST = 100
HOME_INTERNET_ANNUAL_COST = 0

home_staking_annualized_fixed_costs = HOME_HW_COSTS / 5. + HOME_ELECTRICITY_ANNUAL_COST + HOME_INTERNET_ANNUAL_COST

home_staking = {'fixed_costs': home_staking_annualized_fixed_costs / (HOME_VALIDATOR_SIZE * ETH_PRICE_USD),
                'scaling_costs': 0.20}

"""
LST Staking Assumptions:
- Fixed Costs:
    - Negligible, basically the cost of an ERC-20 swap. We round it to 0.
- Scaling Costs:
    - LST Fee: ~10%
    - Taxes:
        - Rebasing Tokens:
            - No forced sell, we set the tax at 0.
"""

lst_staking = {'fixed_costs': 0.,
               'scaling_costs': 0.10}


"""
Institutional Staking Assumptions:
- Fixed Costs:
    - Negligible, basically the cost of stock trade. We round it to 0.
- Scaling Costs:
    - Salaries + Other costs: 5%
    - Taxes:
        - Corporate Tax Rate: 
            - USA (most treasury companies are US based): 21%
    - Total: 0.95 x 0.79 ~ 0.75
"""


institutional_staking = {'fixed_costs': 0.,
                         'scaling_costs': 0.25}
