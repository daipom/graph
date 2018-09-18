import argparse
import datetime
import pandas as pd
from pandas import DataFrame
import plotly.offline as py
import plotly.graph_objs as go


def plot(df: DataFrame, is_x_time: bool=True, time_format: str="%m/%d/%Y %H:%M:%S", to_jupyter: bool=False):
    x_values = \
        df.iloc[:, 0].apply(lambda d: datetime.datetime.strptime(d, time_format)) \
        if is_x_time else \
        df.iloc[:, 0]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=x_values,
                y=df[column_name],
                name=column_name,
                opacity=0.50,
            ) for column_name in list(df.columns)[1:]
        ],
        layout=go.Layout()
    )

    if not to_jupyter:
        py.plot(fig)
    else:
        py.init_notebook_mode(connected=True)
        py.iplot(fig)


def main(file_path: str, encoding: str, is_x_time: bool, time_format: str):
    df = pd.read_csv(file_path, encoding=encoding)
    plot(df, is_x_time=is_x_time, time_format=time_format)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path of csv file to read.", type=str)
    parser.add_argument("--encoding", help="Encoding option of dataframe. Default: utf-16", type=str, default="utf-16")
    parser.add_argument("--is_x_time", help="Whether to handle the first column as time value or not. Default: True", type=bool, default=True)
    parser.add_argument("--time_format", help="Time format for the first column. Default: %m/%d/%Y %H:%M:%S", type=str, default="%m/%d/%Y %H:%M:%S")

    args = parser.parse_args()

    main(args.path, args.encoding, args.is_x_time, args.time_format)
