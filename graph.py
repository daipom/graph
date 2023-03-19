#!/usr/bin/env python3

import sys
import argparse
from datetime import datetime
import pandas as pd
from pandas import DataFrame
import plotly.offline as py
import plotly.graph_objs as go
from typing import List


def create_graph_datalist(
    df: DataFrame,
    path: str = "",
    is_x_time: bool = True,
    time_format: str = "%m/%d/%Y %H:%M:%S",
    use_elapsed: bool = False,
    yaxis_columns: List[str] = None,
    yaxis2_columns: List[str] = None
) -> List[go.Scatter]:

    def strptime(v):
        return datetime.strptime(v, time_format)

    x_values = None
    if is_x_time:
        if use_elapsed:
            start_dt = strptime(df.iloc[0, 0])
            x_values = df.iloc[:, 0].apply(
                lambda d: (strptime(d) - start_dt).total_seconds()
            )
        else:
            x_values = df.iloc[:, 0].apply(
                lambda d: strptime(d)
            )
    else:
        x_values = df.iloc[:, 0]

    is_col1_empty = yaxis_columns is None or not any(yaxis_columns)
    is_col2_empty = yaxis2_columns is None or not any(yaxis2_columns)
    if is_col1_empty and is_col2_empty:
        return [
            go.Scatter(
                x=x_values,
                y=df[column_name],
                name=path + ": " + column_name,
                opacity=0.50,
            ) for column_name in list(df.columns)[1:]
        ]
    else:
        return [
            go.Scatter(
                x=x_values,
                y=df[column_name],
                name=path + ": " + column_name,
                opacity=0.50,
            ) for column_name in yaxis_columns
        ] + [
            go.Scatter(
                x=x_values,
                y=df[column_name],
                name=path + ": " + column_name,
                opacity=0.50,
                yaxis="y2"
            ) for column_name in yaxis2_columns
        ]


def plot(
    dfs: List[DataFrame],
    pathlist: List[str],
    is_x_time: bool = True,
    time_format: str = "%m/%d/%Y %H:%M:%S",
    to_jupyter: bool = False,
    use_elapsed: bool = False,
    yaxis_title: str = "Bytes",
    yaxis2_title: str = "",
    yaxis_columns: List[str] = None,
    yaxis2_columns: List[str] = None
):
    data = []
    for df, path in zip(dfs, pathlist):
        data += create_graph_datalist(
            df,
            path=path,
            is_x_time=is_x_time,
            time_format=time_format,
            use_elapsed=use_elapsed,
            yaxis_columns=yaxis_columns if yaxis_columns else [],
            yaxis2_columns=yaxis2_columns if yaxis2_columns else [],
        )

    fig = go.Figure(
        data=data,
        layout=go.Layout(
            title=pathlist[0] if len(pathlist) == 1 else "",
            xaxis=dict(title="Elapsed [sec]" if use_elapsed else "X"),
            yaxis=dict(title=yaxis_title, exponentformat="SI"),
            yaxis2=dict(
                title=yaxis2_title
                if yaxis2_columns is not None and yaxis2_columns != "None"
                else "",
                exponentformat="SI",
                overlaying="y",
                side="right",
                titlefont=dict(color="rgb(148, 103, 189)"),
                tickfont=dict(color="rgb(148, 103, 189)")
            )
        )
    )

    if not to_jupyter:
        fig.show(
            config=dict(
                showLink=True,
                modeBarButtonsToAdd=["hoverclosest", "hovercompare"]
            )
        )
    else:
        py.init_notebook_mode(connected=True)
        py.iplot(fig)


def main(
    file_path_list: List[str],
    encoding: str,
    is_x_time: bool,
    time_format: str,
    use_elapsed: bool,
    yaxis_title: str,
    yaxis2_title: str,
    yaxis_columns: List[str],
    yaxis2_columns: List[str]
):
    dfs = map(
        lambda path: pd.read_csv(path, encoding=encoding, engine="python"),
        file_path_list
    )
    plot(
        dfs,
        file_path_list,
        is_x_time=is_x_time,
        time_format=time_format,
        use_elapsed=use_elapsed,
        yaxis_title=yaxis_title,
        yaxis2_title=yaxis2_title,
        yaxis_columns=yaxis_columns,
        yaxis2_columns=yaxis2_columns
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("pathlist", help="Path list of csv files to read.", nargs="+")
    parser.add_argument("--encoding", help="Encoding option of dataframe. Default: utf-8", type=str, default="utf-8")
    parser.add_argument("--time-format", help="Time format for the first column.  Can't be used with '--not-timeseries'. Default: %%m/%%d/%%Y %%H:%%M:%%S", type=str, default="%%m/%%d/%%Y %%H:%%M:%%S")
    parser.add_argument("--elapsed", help="Convert the first column to elapsed time. Can't be used with '--not-timeseries'.", action="store_true")
    parser.add_argument("--not-timeseries", help="Doesn't handle the first column as time value, and plot a simple scatter graph.", action="store_true")
    parser.add_argument("--yaxis-title", help="Title of Y axis. Default: Bytes", type=str, default="Bytes")
    parser.add_argument("--yaxis2-title", help="Title of Y axis2.", type=str, default="None")
    parser.add_argument("--yaxis-columns", help="If column names are specified here, then plot those columns to yaxis1. If this and 'yaxis2_columns' are not specified, then plot all columns except the first as X to yaxis1.", nargs="*")
    parser.add_argument("--yaxis2-columns", help="If column names are specified here, then plot those columns to yaxis2.", nargs="*")

    args = parser.parse_args()

    main(
        args.pathlist,
        args.encoding,
        not args.not_timeseries,
        args.time_format,
        args.elapsed,
        args.yaxis_title,
        args.yaxis2_title,
        args.yaxis_columns,
        args.yaxis2_columns
    )
