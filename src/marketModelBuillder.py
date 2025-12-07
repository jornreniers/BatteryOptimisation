import math
import pandas as pd
import numpy as np

from src import Settings
from src.ModelComponents import OptimisationModel as om
from src.ModelComponents import OptimisationVariable as ov
from src.ModelComponents import OptimisationConstraint as oc

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
    # add in degradation cost
    # * 0.5 because each time step is only half an hour
    p = -marketData.loc[
        0 : N - 1, sets.data_struct_colname_price
    ].to_numpy() + sets.degradation_cost_gbpPerMWh * np.ones(shape=(N))
    hh_buy = ov.OptimisationVariable(
        name=sets.varname_halfhour_buy,  # charge
        rel_time_step=1,
        lower_limit=-np.ones(shape=(N,)) * sets.pmax_cha_MW,
        upper_limit=np.zeros(shape=(N,)),
        objective_function=p * 0.5,
        variable_type=ov.VariableType.CONTINUOUS,
    )
    mod.add_variable(hh_buy)

    hh_sell = ov.OptimisationVariable(
        name=sets.varname_halfhour_sell,  # discharge
        rel_time_step=1,
        lower_limit=np.zeros(shape=(N,)),
        upper_limit=np.ones(shape=(N,)) * sets.pmax_dis_MW,
        objective_function=p * 0.5,
        variable_type=ov.VariableType.CONTINUOUS,
    )
    mod.add_variable(hh_sell)

    # sign is 0 for charge (negative), and 1 for discharge (positive)
    power_sign = ov.OptimisationVariable(
        name=sets.varname_power_sign,
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
    discharge_constraint = oc.OptimisationConstraint(
        name="binary_for_discharge",
        variable_factors={
            sets.varname_halfhour_sell: 1,
            sets.varname_power_sign: -mod.variables[
                sets.varname_halfhour_sell
            ].upper_limit[0],
        },
        lower_limit=-np.inf,
        upper_limit=0,
    )
    mod.add_constraint(c=discharge_constraint, N=N)

    # ll(1-sign) <= Pcharge <= ul
    # ll <= Pcharge + sign*ll <= inf
    charge_constraint = oc.OptimisationConstraint(
        name="binary_for_charge",
        variable_factors={
            sets.varname_halfhour_buy: 1,
            sets.varname_power_sign: -mod.variables[
                sets.varname_halfhour_buy
            ].lower_limit[0],
        },
        lower_limit=mod.variables[sets.varname_halfhour_buy].lower_limit[0],
        upper_limit=np.inf,
    )
    mod.add_constraint(c=charge_constraint, N=N)

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

    p = -marketData.loc[
        0 : n - 1, sets.data_struct_colname_price
    ].to_numpy() + sets.degradation_cost_gbpPerMWh * np.ones(shape=(n))
    h_buy = ov.OptimisationVariable(
        name=sets.varname_hour_buy,  # charge
        rel_time_step=rel_time_step,
        lower_limit=-np.ones(shape=(n,)) * sets.pmax_cha_MW,
        upper_limit=np.zeros(shape=(n,)),
        objective_function=p,
        variable_type=ov.VariableType.CONTINUOUS,
    )
    mod.add_variable(h_buy)

    h_sell = ov.OptimisationVariable(
        name=sets.varname_hour_sell,  # discharge
        rel_time_step=rel_time_step,
        lower_limit=np.zeros(shape=(n,)),
        upper_limit=np.ones(shape=(n,)) * sets.pmax_dis_MW,
        objective_function=p,
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
    discharge_constraint = oc.OptimisationConstraint(
        name="binary_for_discharge_hour",
        variable_factors={
            sets.varname_hour_sell: 1,
            sets.varname_power_sign: -mod.variables[sets.varname_hour_sell].upper_limit[
                0
            ],
        },
        lower_limit=-np.inf,
        upper_limit=0,
    )
    mod.add_constraint(c=discharge_constraint, N=N)

    # ll(1-sign) <= Pcharge <= ul
    # ll <= Pcharge + sign*ll <= inf
    charge_constraint = oc.OptimisationConstraint(
        name="binary_for_charge_hour",
        variable_factors={
            sets.varname_hour_buy: 1,
            sets.varname_power_sign: -mod.variables[sets.varname_hour_buy].lower_limit[
                0
            ],
        },
        lower_limit=mod.variables[sets.varname_hour_buy].lower_limit[0],
        upper_limit=np.inf,
    )
    mod.add_constraint(c=charge_constraint, N=N)

    return mod
