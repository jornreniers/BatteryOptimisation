import os
import numpy as np
import pandas as pd
from scipy import optimize
from plotly.subplots import make_subplots


from plotly import graph_objects as go
from plotly import express as px
from src import Settings
from src import OptimisationModel as om
from src import OptimisationVariable as ov


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

    # plot power bought & sold separately to validate constraints are met
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=["half hour market", "hour market"],
        specs=[
            [{"secondary_y": True}],
            [{"secondary_y": True}],
        ],
    )
    # Half-hour market
    thh = dfs[0].loc[0 : N - 1, sets.data_struct_colname_time].to_numpy()
    fig.add_trace(
        go.Scatter(x=thh, y=vars["hh_sell"], name="sold"),
        row=1,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=thh, y=vars["hh_buy"], name="bought"),
        row=1,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=thh,
            y=dfs[0].loc[0 : N - 1, sets.data_struct_colname_price].to_numpy(),
            name="price",
        ),
        row=1,
        col=1,
        secondary_y=True,
    )
    # Hourly market
    rel_time_step = 2
    n = (int)(N / rel_time_step)
    th = dfs[1].loc[0 : n - 1, sets.data_struct_colname_time].to_numpy()
    fig.add_trace(
        go.Scatter(x=th, y=vars["h_sell"], name="sold"),
        row=2,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=th, y=vars["h_buy"], name="bought"),
        row=2,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=th,
            y=dfs[1].loc[0 : n - 1, sets.data_struct_colname_price].to_numpy(),
            name="price",
        ),
        row=2,
        col=1,
        secondary_y=True,
    )
    fig.write_html("Results/market_buy_sell_detail.html")

    # plot net power of each market to give an overview
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=["half hour market", "hour market"],
        specs=[
            [{"secondary_y": True}],
            [{"secondary_y": True}],
        ],
    )
    # Half-hour market
    fig.add_trace(
        go.Bar(
            x=thh, y=vars["hh_sell"] + vars["hh_buy"], name="Volume, pos=sell, neg=buy"
        ),
        row=1,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=thh,
            y=dfs[0].loc[0 : N - 1, sets.data_struct_colname_price].to_numpy(),
            name="price",
        ),
        row=1,
        col=1,
        secondary_y=True,
    )
    # Hourly market
    fig.add_trace(
        go.Bar(
            x=th, y=vars["h_sell"] + vars["h_buy"], name="Volume, pos=sell, neg=buy"
        ),
        row=2,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=th,
            y=dfs[1].loc[0 : n - 1, sets.data_struct_colname_price].to_numpy(),
            name="price",
        ),
        row=2,
        col=1,
        secondary_y=True,
    )
    fig.write_html("Results/market_overview.html")


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
    phalf = vars["hh_sell"] + vars["hh_buy"]
    phour = vars["h_sell"] + vars["h_buy"]
    p = phalf + np.repeat(phour, 2)

    fig.add_trace(
        go.Bar(
            x=thh, y=p, name="net traded Volume, pos=sell=discharge, neg=buy=charge"
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=thh,
            y=vars["soc"],
            name="soc",
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

    vars = dict[str, np.ndarray]()
    for v in mod.variables.values():
        vars[v.name] = result.x[
            v.start_index : v.start_index + (int)(N / v.relative_time_step)
        ]
    thh = dfs[0].loc[0 : N - 1, sets.data_struct_colname_time].to_numpy()
    # Hourly market
    rel_time_step = 2
    n = (int)(N / rel_time_step)
    th = dfs[1].loc[0 : n - 1, sets.data_struct_colname_time].to_numpy()

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Scatter(
            x=thh,
            y=dfs[0].loc[0 : N - 1, sets.data_struct_colname_price].to_numpy(),
            name="half-hourly price",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=th,
            y=dfs[1].loc[0 : n - 1, sets.data_struct_colname_price].to_numpy(),
            name="hourly price",
        ),
        row=1,
        col=1,
    )
    fig.write_html("Results/price_detail.html")
