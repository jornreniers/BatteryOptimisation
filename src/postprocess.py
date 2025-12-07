import os
import numpy as np
import pandas as pd
from scipy import optimize
from plotly.subplots import make_subplots


from plotly import graph_objects as go
from src import Settings
from src.ModelComponents import OptimisationModel as om

"""
Plot traded volumes and revenue
"""


def plot_market_details(
    mod: om.OptimisationModel,
    result: optimize.OptimizeResult,
    N: int,
    dfs: list[pd.DataFrame],
    sets: Settings.Settings,
):
    # extract the individual variables
    vars = dict[str, np.ndarray]()
    for v in mod.variables.values():
        vars[v.name] = result.x[
            v.start_index : v.start_index + (int)(N / v.relative_time_step)
        ]

    thh = dfs[0].loc[0 : N - 1, sets.data_struct_colname_time].to_numpy()
    n = (int)(N / mod.variables[sets.varname_hour_buy].relative_time_step)
    th = dfs[1].loc[0 : n - 1, sets.data_struct_colname_time].to_numpy()

    # # plot power bought & sold separately to validate constraints are met
    # fig = make_subplots(
    #     rows=2,
    #     cols=1,
    #     shared_xaxes=True,
    #     subplot_titles=["half hour market", "hour market"],
    #     specs=[
    #         [{"secondary_y": True}],
    #         [{"secondary_y": True}],
    #     ],
    # )
    # # Half-hour market
    #
    # fig.add_trace(
    #     go.Scatter(x=thh, y=vars[sets.varname_halfhour_sell], name="sold"),
    #     row=1,
    #     col=1,
    #     secondary_y=False,
    # )
    # fig.add_trace(
    #     go.Scatter(x=thh, y=vars[sets.varname_halfhour_buy], name="bought"),
    #     row=1,
    #     col=1,
    #     secondary_y=False,
    # )
    # fig.add_trace(
    #     go.Scatter(
    #         x=thh,
    #         y=dfs[0].loc[0 : N - 1, sets.data_struct_colname_price].to_numpy(),
    #         name="price",
    #     ),
    #     row=1,
    #     col=1,
    #     secondary_y=True,
    # )
    # # Hourly market
    # rel_time_step = 2
    #
    # fig.add_trace(
    #     go.Scatter(x=th, y=vars[sets.varname_hour_sell], name="sold"),
    #     row=2,
    #     col=1,
    #     secondary_y=False,
    # )
    # fig.add_trace(
    #     go.Scatter(x=th, y=vars[sets.varname_hour_buy], name="bought"),
    #     row=2,
    #     col=1,
    #     secondary_y=False,
    # )
    # fig.add_trace(
    #     go.Scatter(
    #         x=th,
    #         y=dfs[1].loc[0 : n - 1, sets.data_struct_colname_price].to_numpy(),
    #         name="price",
    #     ),
    #     row=2,
    #     col=1,
    #     secondary_y=True,
    # )
    # fig.write_html("Results/market_buy_sell_detail.html")

    # plot net power of each market to give an overview
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=["half hour market", "hour market", "cumulative revenue"],
        specs=[
            [{"secondary_y": True}],
            [{"secondary_y": True}],
            [{"secondary_y": False}],
        ],
    )
    # Half-hour market
    fig.add_trace(
        go.Bar(
            x=thh,
            y=vars[sets.varname_halfhour_sell] + vars[sets.varname_halfhour_buy],
            name="Volume [MW], pos=sell, neg=buy",
        ),
        row=1,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=thh,
            y=dfs[0].loc[0 : N - 1, sets.data_struct_colname_price].to_numpy(),
            name="price [£/MWh]",
        ),
        row=1,
        col=1,
        secondary_y=True,
    )
    # Hourly market
    fig.add_trace(
        go.Bar(
            x=th,
            y=vars[sets.varname_hour_sell] + vars[sets.varname_hour_buy],
            name="Volume [MW], pos=sell, neg=buy",
        ),
        row=2,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=th,
            y=dfs[1].loc[0 : n - 1, sets.data_struct_colname_price].to_numpy(),
            name="price [£/MWh]",
        ),
        row=2,
        col=1,
        secondary_y=True,
    )

    # Compute the total profit
    # keep the hourly revenue constant over a half-hour period
    revenue_hh = (
        (vars[sets.varname_halfhour_sell] + vars[sets.varname_halfhour_buy])
        * dfs[0].loc[0 : N - 1, sets.data_struct_colname_price].to_numpy()
        * 0.2
    )
    revenue_h = (vars[sets.varname_hour_sell] + vars[sets.varname_hour_buy]) * dfs[
        1
    ].loc[0 : n - 1, sets.data_struct_colname_price].to_numpy()
    revenue_h = np.repeat(revenue_h, 2)
    profit = np.cumsum(revenue_h + revenue_hh)
    fig.add_trace(
        go.Scatter(
            x=thh,
            y=profit,
            name="revenue [£]",
        ),
        row=3,
        col=1,
    )

    fig.write_html("Results/market_overview.html")


"""
Plot the net traded power and SoC.
Note that the battery power (which affects SoC) is different
from the net traded power due to the losses.
"""


def plot_battery_details(
    mod: om.OptimisationModel,
    result: optimize.OptimizeResult,
    N: int,
    dfs: list[pd.DataFrame],
    sets: Settings.Settings,
):
    # extract the individual variables
    vars = dict[str, np.ndarray]()
    for v in mod.variables.values():
        vars[v.name] = result.x[
            v.start_index : v.start_index + (int)(N / v.relative_time_step)
        ]

    # plot power bought & sold separately to validate constraints are met
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=["total power", "battery SoC"],
    )

    thh = dfs[0].loc[0 : N - 1, sets.data_struct_colname_time].to_numpy()
    phalf = vars[sets.varname_halfhour_sell] + vars[sets.varname_halfhour_buy]
    phour = vars[sets.varname_hour_sell] + vars[sets.varname_hour_buy]
    p = phalf + np.repeat(phour, 2)

    fig.add_trace(
        go.Bar(
            x=thh,
            y=p,
            name="net traded Volume [MW], pos=sell=discharge, neg=buy=charge",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=thh,
            y=vars[sets.varname_soc],
            name="soc =[-]",
        ),
        row=2,
        col=1,
    )
    fig.write_html("Results/battery_overview.html")


def plot_results(
    mod: om.OptimisationModel,
    result: optimize.OptimizeResult,
    N: int,
    dfs: list[pd.DataFrame],
    sets: Settings.Settings,
):
    if not (os.path.exists("Results")):
        os.makedirs("Results")

    plot_market_details(
        mod=mod,
        result=result,
        N=N,
        dfs=dfs,
        sets=sets,
    )

    plot_battery_details(
        mod=mod,
        result=result,
        N=N,
        dfs=dfs,
        sets=sets,
    )
