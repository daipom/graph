#!/usr/bin/env python3

# Copyright (C) 2023 Daijiro Fukuda <fukuda@clear-code.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
    time_format: str = "%Y-%m-%d %H:%M:%S %z",
    use_elapsed: bool = False,
    with_markers: bool = False,
    yaxis_columns: List[str] = [],
    yaxis2_columns: List[str] = [],
    minimum_required_value: int = None,
) -> List[go.Scatter]:

    def strptime(v):
        return datetime.strptime(v, time_format)

    def scatter_name(column_name):
        return f"{path}: {column_name}" if path else column_name

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

    mode = "lines"
    if with_markers:
        mode += "+markers"

    is_col1_empty = yaxis_columns is None or not any(yaxis_columns)
    is_col2_empty = yaxis2_columns is None or not any(yaxis2_columns)
    if is_col1_empty and is_col2_empty:
        return [
            go.Scatter(
                x=x_values,
                y=df[column_name],
                name=scatter_name(column_name),
                opacity=0.50,
                mode=mode,
            ) for column_name in list(df.columns)[1:]
            if minimum_required_value is None or df[column_name].max() >= minimum_required_value
        ]
    else:
        return [
            go.Scatter(
                x=x_values,
                y=df[column_name],
                name=scatter_name(column_name),
                opacity=0.50,
                mode=mode,
            ) for column_name in yaxis_columns
            if column_name in df.columns
            if minimum_required_value is None or df[column_name].max() >= minimum_required_value
        ] + [
            go.Scatter(
                x=x_values,
                y=df[column_name],
                name=scatter_name(column_name),
                opacity=0.50,
                mode=mode,
                yaxis="y2",
            ) for column_name in yaxis2_columns
            if column_name in df.columns
            if minimum_required_value is None or df[column_name].max() >= minimum_required_value
        ]


def plot(
    dfs: List[DataFrame],
    pathlist: List[str],
    is_x_time: bool = True,
    time_format: str = "%Y-%m-%d %H:%M:%S %z",
    to_jupyter: bool = False,
    use_elapsed: bool = False,
    with_markers: bool = False,
    graph_title: str = None,
    xaxis_title: str = None,
    yaxis_title: str = "Bytes",
    yaxis2_title: str = "",
    yaxis_columns: List[str] = None,
    yaxis2_columns: List[str] = None,
    minimum_required_value: int = None,
):
    data = []
    for df, path in zip(dfs, pathlist):
        data += create_graph_datalist(
            df,
            path=None if len(pathlist) == 1 else path,
            is_x_time=is_x_time,
            time_format=time_format,
            use_elapsed=use_elapsed,
            with_markers=with_markers,
            yaxis_columns=yaxis_columns if yaxis_columns else [],
            yaxis2_columns=yaxis2_columns if yaxis2_columns else [],
            minimum_required_value=minimum_required_value,
        )

    if graph_title is None:
        graph_title = pathlist[0] if len(pathlist) == 1 else ""

    if xaxis_title is None:
        xaxis_title = "Elapsed [sec]" if use_elapsed else dfs[0].columns[0]

    fig = go.Figure(
        data=data,
        layout=go.Layout(
            title=graph_title,
            xaxis=dict(title=xaxis_title),
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
        fig.write_html(
            file="temp-plot.html",
            auto_open=True,
            config=dict(
                editable=True,
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
    graph_title: str,
    xaxis_title: str,
    yaxis_title: str,
    yaxis2_title: str,
    yaxis_columns: List[str],
    yaxis2_columns: List[str],
    with_markers: bool,
    minimum_required_value: int,
):
    dfs = [
        pd.read_csv(path, encoding=encoding, engine="python")
        for path in file_path_list
    ]
    plot(
        dfs,
        file_path_list,
        is_x_time=is_x_time,
        time_format=time_format,
        use_elapsed=use_elapsed,
        graph_title=graph_title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        yaxis2_title=yaxis2_title,
        yaxis_columns=yaxis_columns,
        yaxis2_columns=yaxis2_columns,
        with_markers=with_markers,
        minimum_required_value=minimum_required_value,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("pathlist", help="Path list of csv files to read.", nargs="+")
    parser.add_argument("--encoding", help="Encoding option of dataframe. Default: utf-8", type=str, default="utf-8")
    parser.add_argument("--time-format", help="Time format for the first column.  Can't be used with '--not-timeseries'. Default: %%Y-%%m-%%d %%H:%%M:%%S %%z", type=str, default="%Y-%m-%d %H:%M:%S %z")
    parser.add_argument("--elapsed", help="Convert the first column to elapsed time. Can't be used with '--not-timeseries'.", action="store_true")
    parser.add_argument("--with-markers", help="Display lines with markers.", action="store_true")
    parser.add_argument("--not-timeseries", help="Doesn't handle the first column as time value, and plot a simple scatter graph.", action="store_true")
    parser.add_argument("--graph-title", help="Title of graph. By default, the filepath is used as a title with a single pathlist.", type=str, default=None)
    parser.add_argument("--xaxis-title", help="Title of X axis. By default, the first column name is used.", type=str, default=None)
    parser.add_argument("--yaxis-title", help="Title of Y axis. Default: Bytes", type=str, default="Bytes")
    parser.add_argument("--yaxis2-title", help="Title of Y axis2.", type=str, default="None")
    parser.add_argument("--yaxis-columns", help="If column names are specified here, then plot those columns to yaxis1. If this and 'yaxis2_columns' are not specified, then plot all columns except the first as X to yaxis1.", nargs="*")
    parser.add_argument("--yaxis2-columns", help="If column names are specified here, then plot those columns to yaxis2.", nargs="*")
    parser.add_argument("--minimum-required-value", help="Exclude columns with the max value less than this value. Default: None", type=int, default=None)

    args = parser.parse_args()

    main(
        args.pathlist,
        args.encoding,
        not args.not_timeseries,
        args.time_format,
        args.elapsed,
        args.graph_title,
        args.xaxis_title,
        args.yaxis_title,
        args.yaxis2_title,
        args.yaxis_columns,
        args.yaxis2_columns,
        args.with_markers,
        args.minimum_required_value,
    )
