from src import preprocess
from src import Settings
from src.ModelComponents import OptimisationModel as om
from src import marketModelBuillder as mmb
from src import batteryModelBuillder as bmb
from src import plotResults as pl


def main():
    sets = Settings.Settings()
    N = 48 * 7

    dfs = preprocess.preprocess_run(sets=sets)

    print("Build the model")
    mod = om.OptimisationModel()
    mod = mmb.add_halfhour_market(marketData=dfs[0], sets=sets, mod=mod, N=N)
    mod = mmb.add_hour_market(marketData=dfs[1], sets=sets, mod=mod, N=N)
    mod = bmb.add_soc(sets=sets, mod=mod, N=N)
    mod = bmb.add_power_limit(sets=sets, mod=mod, N=N)

    # print(mod.objective_function)

    print("Start optimisation")
    res = mod.optimise()

    # # print(res.status)
    # print(f"The objective function is {res.fun} which is achieved with")
    # for v in mod.variables.values():
    #     print(
    #         f"{v.name} with values {res.x[v.start_index : v.start_index + (int)(N / v.relative_time_step)]}"
    #     )

    print("Start plotting results")
    pl.plot_results(mod=mod, result=res, N=N, dfs=dfs, sets=sets)


if __name__ == "__main__":
    main()
