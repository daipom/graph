import argparse
from datetime import datetime
import pandas as pd
from pandas import DataFrame
import plotly.offline as py
import plotly.graph_objs as go
from typing import List


def create_graph_datalist(df: DataFrame, path: str="", is_x_time: bool=True, time_format: str="%m/%d/%Y %H:%M:%S", use_elapsed: bool=False, specified_column: str="") -> List[go.Scatter]:
    x_values = None
    if is_x_time:
        if use_elapsed:
            startdatetime = datetime.strptime(df.iloc[0, 0], time_format)
            x_values = df.iloc[:, 0].apply(lambda d: (datetime.strptime(d, time_format) - startdatetime).total_seconds())
        else:
            x_values = df.iloc[:, 0].apply(lambda d: datetime.strptime(d, time_format))
    else:
        x_values = df.iloc[:, 0]

    if specified_column is None or specified_column == "None" or specified_column == "":
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
                y=df[specified_column],
                name=path + ": " + specified_column,
                opacity=0.50,
            )
        ]


def plot(dfs: List[DataFrame], pathlist: List[str], is_x_time: bool=True, time_format: str="%m/%d/%Y %H:%M:%S", to_jupyter: bool=False, specified_column: str="", use_elapsed: bool=False):
    data = []
    for df, path in zip(dfs, pathlist):
        data += create_graph_datalist(df, path=path, is_x_time=is_x_time, time_format=time_format, use_elapsed=use_elapsed, specified_column=specified_column)

    fig = go.Figure(
        data=data,
        layout=go.Layout(
            title="",
            xaxis=dict(title="Elapsed [sec]"),
            yaxis=dict(title="Bytes", exponentformat="SI")
        )
    )

    if not to_jupyter:
        py.plot(fig)
    else:
        py.init_notebook_mode(connected=True)
        py.iplot(fig)


def main(file_path_list: List[str], encoding: str, is_x_time: bool, time_format: str, specified_column: str, use_elapsed: bool):
    dfs = map(lambda path: pd.read_csv(path, encoding=encoding), file_path_list)
    # df = pd.read_csv(file_path, encoding=encoding)
    plot(dfs, file_path_list, is_x_time=is_x_time, time_format=time_format, specified_column=specified_column, use_elapsed=use_elapsed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path_list", help="Path list of csv files to read.", nargs="*")
    parser.add_argument("--encoding", help="Encoding option of dataframe. Default: utf-16", type=str, default="utf-16")
    parser.add_argument("--is_x_time", help="To handle the first column as time value. Default: True", type=lambda s: s.lower() in ["true", "1", "yes"], default="True")
    parser.add_argument("--time_format", help="Time format for the first column. Default: %m/%d/%Y %H:%M:%S", type=str, default="%m/%d/%Y %H:%M:%S")
    parser.add_argument("--specify_column", help="If column name is specified here, then only plot the column as Y every one file. If not specified, then plot all columns as Y except the first column (X).", type=str, default="None")
    parser.add_argument("--elapsed", help="To convert the first column to elapsed time. Default: False", type=lambda s: s.lower() in ["true", "1", "yes"], default="False")

    args = parser.parse_args()

    main(args.path_list, args.encoding, args.is_x_time, args.time_format, args.specify_column, args.elapsed)
