import pandas as pd
import numpy as np

from src import Settings
from src import OptimisationModel as om
from src import OptimisationVariable as ov


def run(dfs: list[pd.DataFrame]):
    mod = om.OptimisationModel()
    sets = Settings.Settings()

    N = 10

    # print(dfs[0].head())
    # print(dfs[0][1])

    hh_market = ov.OptimisationVariable(
        name="hh_market",
        rel_time_step=1,
        lower_limit=-np.ones(shape=(N,)) * sets.pmax_cha_MW,
        upper_limit=np.ones(shape=(N,)) * sets.pmax_dis_MW,
        objective_function=dfs[0]
        .loc[0 : N - 1, sets.data_struct_colname_price]
        .to_numpy(),
    )
    mod.add_variable(hh_market)

    res = mod.optimise()
    print(res.status)
    print(f"The objective function is {res.fun} which is achieved with")
    for v in mod.variables:
        print(
            f"{v.name} with values {res.x[v.start_index : v.start_index + N * v.relative_time_step]}"
        )
