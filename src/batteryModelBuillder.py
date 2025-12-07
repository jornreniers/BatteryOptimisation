import math
import numpy as np

from src import Settings
from src.ModelComponents import OptimisationModel as om
from src.ModelComponents import OptimisationVariable as ov
from src.ModelComponents import OptimisationConstraint as oc


def add_soc(
    sets: Settings.Settings, mod: om.OptimisationModel, N: int
) -> om.OptimisationModel:
    # buying = charging power = negative (and costs money)
    # selling = discharging = positive (and earns money)
    soc = ov.OptimisationVariable(
        name=sets.varname_soc,
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
    # NOTE: this constraint looks differently for the first time step
    # and it has off-diagonal elements (t-1)
    # we therefore add it manually
    for i in range(N):
        k = math.floor(i / 2)
        # there are 4 powers
        # when discharging (selling) the battery loses more energy so P/eta
        # when charging (buying) the battery gains less energy so P * eta
        a = np.zeros_like(mod.lower_limit)
        a[mod.variables[sets.varname_halfhour_sell].start_index + i] = (
            cap / sets.eta_dis
        )
        a[mod.variables[sets.varname_halfhour_buy].start_index + i] = cap * sets.eta_cha
        a[mod.variables[sets.varname_hour_sell].start_index + k] = cap / sets.eta_dis
        a[mod.variables[sets.varname_hour_buy].start_index + k] = cap * sets.eta_cha
        a[mod.variables[sets.varname_soc].start_index + i] = -1
        b = -sets.soc_ini
        if i > 0:
            a[mod.variables[sets.varname_soc].start_index + i - 1] = 1
            b = 0

        mod.add_constraint_manual(arow=a, lb=b, ub=b)

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
    # discharge_battery_power for discharge
    discharge_power = oc.OptimisationConstraint(
        name="discharge_battery_power",
        variable_factors={
            sets.varname_halfhour_sell: 1,
            sets.varname_hour_sell: 1,
        },
        lower_limit=0,
        upper_limit=sets.pmax_dis_MW,
    )
    mod.add_constraint(c=discharge_power, N=N)

    # constraint for charge
    charge_power = oc.OptimisationConstraint(
        name="charge_battery_power",
        variable_factors={
            sets.varname_halfhour_buy: 1,
            sets.varname_hour_buy: 1,
        },
        lower_limit=-sets.pmax_cha_MW,
        upper_limit=0,
    )
    mod.add_constraint(c=charge_power, N=N)

    return mod
