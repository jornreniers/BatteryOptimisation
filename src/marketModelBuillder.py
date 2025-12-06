import math
import pandas as pd
import numpy as np

from src import Settings
from src import OptimisationModel as om
from src import OptimisationVariable as ov

"""
Add basic trading on the half-hour market to the model.

This adds three optimisation variables:
buying (charge power)
selling (discharge power)
sign (binary variable indicating whether we're buying or selling)
"""


def add_halfhour_market(
    marketData: pd.DataFrame, sets: Settings.Settings, mod: om.OptimisationModel, N: int
) -> om.OptimisationModel:
    # buying = charging power = negative (and costs money)
    # selling = discharging = positive (and earns money)
    # objective = -price because we minimise
    # * 0.5 because each time step is only half an hour
    hh_buy = ov.OptimisationVariable(
        name="hh_buy",  # charge
        rel_time_step=1,
        lower_limit=-np.ones(shape=(N,)) * sets.pmax_cha_MW,
        upper_limit=np.zeros(shape=(N,)),
        objective_function=-marketData.loc[
            0 : N - 1, sets.data_struct_colname_price
        ].to_numpy()
        * 0.5,
        variable_type=ov.VariableType.CONTINUOUS,
    )
    mod.add_variable(hh_buy)

    hh_sell = ov.OptimisationVariable(
        name="hh_sell",  # discharge
        rel_time_step=1,
        lower_limit=np.zeros(shape=(N,)),
        upper_limit=np.ones(shape=(N,)) * sets.pmax_dis_MW,
        objective_function=-marketData.loc[
            0 : N - 1, sets.data_struct_colname_price
        ].to_numpy()
        * 0.5,
        variable_type=ov.VariableType.CONTINUOUS,
    )
    mod.add_variable(hh_sell)

    # sign is 0 for charge (negative), and 1 for discharge (positive)
    power_sign = ov.OptimisationVariable(
        name="sign",
        rel_time_step=1,
        lower_limit=np.zeros(shape=(N,)),
        upper_limit=np.ones(shape=(N,)),
        objective_function=np.zeros(shape=(N,)),
        variable_type=ov.VariableType.INTEGER,
    )
    mod.add_variable(power_sign)

    # Constraints to set the binary variable:
    # sign is 0 for charge (negative), and 1 for discharge (positive)
    # ll = lower limit, ul = upper limit on a varable.
    # ll <= Pdischarge <= ul * sign
    # -inf <= Pdischarge - ul*sign <= 0
    for i in range(N):
        a = np.zeros_like(mod.lower_limit)
        a[mod.variables["hh_sell"].start_index + i] = 1
        a[mod.variables["sign"].start_index + i] = -mod.variables[
            "hh_sell"
        ].upper_limit[i]
        mod.add_constraint(arow=a, lb=-np.inf, ub=0)
    # ll(1-sign) <= Pcharge <= ul
    # ll <= Pcharge + sign*ll <= inf
    for i in range(N):
        a = np.zeros_like(mod.lower_limit)
        a[mod.variables["hh_buy"].start_index + i] = 1
        a[mod.variables["sign"].start_index + i] = mod.variables["hh_buy"].lower_limit[
            i
        ]
        mod.add_constraint(arow=a, lb=mod.variables["hh_buy"].lower_limit[i], ub=np.inf)

    return mod


"""
Same but for the hour market.

Note that we don't re-create the binary variables, 
we just add constraints for the actions in the hour market too
"""


def add_hour_market(
    marketData: pd.DataFrame, sets: Settings.Settings, mod: om.OptimisationModel, N: int
) -> om.OptimisationModel:
    # buying = charging power = negative (and costs money)
    # selling = discharging = positive (and earns money)
    # objective = -price because we minimise
    rel_time_step = 2
    n = (int)(N / rel_time_step)

    h_buy = ov.OptimisationVariable(
        name="h_buy",  # charge
        rel_time_step=rel_time_step,
        lower_limit=-np.ones(shape=(n,)) * sets.pmax_cha_MW,
        upper_limit=np.zeros(shape=(n,)),
        objective_function=-marketData.loc[
            0 : n - 1, sets.data_struct_colname_price
        ].to_numpy(),
        variable_type=ov.VariableType.CONTINUOUS,
    )
    mod.add_variable(h_buy)

    h_sell = ov.OptimisationVariable(
        name="h_sell",  # discharge
        rel_time_step=rel_time_step,
        lower_limit=np.zeros(shape=(n,)),
        upper_limit=np.ones(shape=(n,)) * sets.pmax_dis_MW,
        objective_function=-marketData.loc[
            0 : n - 1, sets.data_struct_colname_price
        ].to_numpy(),
        variable_type=ov.VariableType.CONTINUOUS,
    )
    mod.add_variable(h_sell)

    # The binary variable to charge and discharge
    # from the half-hourly market can be re-used.
    # Note that we do need one constraint per half-hour
    # ie two per hourly action
    # otherwise the half-hourly market could take an
    # illegal action in the second half-hour
    # ll = lower limit, ul = upper limit on a varable.
    # ll <= Pdischarge <= ul * sign
    # -inf <= Pdischarge - ul*sign <= 0
    for i in range(N):
        k = math.floor(i / 2)
        a = np.zeros_like(mod.lower_limit)
        a[mod.variables["h_sell"].start_index + k] = 1
        a[mod.variables["sign"].start_index + i] = -mod.variables["h_sell"].upper_limit[
            k
        ]
        mod.add_constraint(arow=a, lb=-np.inf, ub=0)
    # ll(1-sign) <= Pcharge <= ul
    # ll <= Pcharge + sign*ll <= inf
    for i in range(N):
        k = math.floor(i / 2)
        a = np.zeros_like(mod.lower_limit)
        a[mod.variables["h_buy"].start_index + k] = 1
        a[mod.variables["sign"].start_index + i] = mod.variables["h_buy"].lower_limit[k]
        mod.add_constraint(arow=a, lb=mod.variables["h_buy"].lower_limit[k], ub=np.inf)

    return mod
