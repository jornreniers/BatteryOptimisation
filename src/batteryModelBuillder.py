import math
import numpy as np

from src import Settings
from src import OptimisationModel as om
from src import OptimisationVariable as ov

"""
Add the SoC at the end of the period to the model
"""


def add_soc(
    sets: Settings.Settings, mod: om.OptimisationModel, N: int
) -> om.OptimisationModel:
    # buying = charging power = negative (and costs money)
    # selling = discharging = positive (and earns money)
    soc = ov.OptimisationVariable(
        name="soc",  # charge
        rel_time_step=1,
        lower_limit=np.zeros(shape=(N,)),
        upper_limit=np.ones(shape=(N,)),
        objective_function=np.zeros(shape=(N,)),
        variable_type=ov.VariableType.CONTINUOUS,
    )
    mod.add_variable(soc)

    # Constraint for SoC:
    # soc(t) = soc(t-1) - P / capacity * time_step
    # capacity is in MWh, power in MW so the time step is 0.5
    cap = -0.5 / sets.capacity_MWh
    for i in range(N):
        k = math.floor(i / 2)
        # there are 4 powers
        # when discharging (selling) the battery loses more energy so P/eta
        # when charging (buying) the battery gains less energy so P * eta
        a = np.zeros_like(mod.lower_limit)
        a[mod.variables["hh_sell"].start_index + i] = cap / sets.eta_dis
        a[mod.variables["hh_buy"].start_index + i] = cap * sets.eta_cha
        a[mod.variables["h_sell"].start_index + k] = cap / sets.eta_dis
        a[mod.variables["h_buy"].start_index + k] = cap * sets.eta_cha
        a[mod.variables["soc"].start_index + i] = -1
        b = -sets.soc_ini
        if i > 0:
            a[mod.variables["soc"].start_index + i - 1] = 1
            b = 0

        mod.add_constraint(arow=a, lb=b, ub=b)

    return mod


"""
Previously we constrained the individual powers to each market
However, the battery receives the sum of both which needs to be below its limit

NOTE: it is not specified whether the maximum power applies before or after losses
I assume the power limit is on the "output" of the battery, ie the interface with the grid
which means the traded power is limited to the specified limit.
This means that if the battery is discharging, the battery itself will see a slightly
higher power, up to 2 MW / 0.95  or about 2.1 MW
"""


def add_power_limit(
    sets: Settings.Settings, mod: om.OptimisationModel, N: int
) -> om.OptimisationModel:
    # constraint for discharge
    for i in range(N):
        k = math.floor(i / 2)
        a = np.zeros_like(mod.lower_limit)
        a[mod.variables["hh_sell"].start_index + i] = 1
        a[mod.variables["h_sell"].start_index + k] = 1

        mod.add_constraint(arow=a, lb=0, ub=sets.pmax_dis_MW)

    # constraint for charge
    for i in range(N):
        k = math.floor(i / 2)
        # there are 4 powers
        # when discharging (selling) the battery loses more energy so P/eta
        # when charging (buying) the battery gains less energy so P * eta
        a = np.zeros_like(mod.lower_limit)
        a[mod.variables["hh_buy"].start_index + i] = 1
        a[mod.variables["h_buy"].start_index + k] = 1

        mod.add_constraint(arow=a, lb=-sets.pmax_cha_MW, ub=0)

    return mod
