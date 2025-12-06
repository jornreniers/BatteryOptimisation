from src import preprocess
from src import Settings
from src import modelBuilder as mb
from src import plotResults as pl


def main():
    sets = Settings.Settings()
    N = 48 * 7

    print("Build the model")
    dfs = preprocess.preprocess_run(sets=sets)
    mod = mb.run(dfs=dfs, sets=sets, N=N)

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
