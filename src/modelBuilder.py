import pandas as pd

from src import Settings
from src import OptimisationModel as om
from src import marketModelBuillder as mmb
from src import batteryModelBuillder as bmb


def run(
    dfs: list[pd.DataFrame], sets: Settings.Settings, N: int
) -> om.OptimisationModel:
    mod = om.OptimisationModel()

    mod = mmb.add_halfhour_market(marketData=dfs[0], sets=sets, mod=mod, N=N)
    mod = mmb.add_hour_market(marketData=dfs[1], sets=sets, mod=mod, N=N)
    mod = bmb.add_soc(sets=sets, mod=mod, N=N)
    mod = bmb.add_power_limit(sets=sets, mod=mod, N=N)

    return mod
