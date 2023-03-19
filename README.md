# Graph

This is a Python script to easily create a scatter graph using [plotly](https://plotly.com/python/).

`plotly` is a very useful library to create a graph as a standalone HTML file.
However, it is difficult for me to remember the many options of `plotly`.

I have made it easy to create graphs for very common cases.
You can use this script to create a common scatter plot quickly and easily.

* Read one or multiple CSV file(s).
  * When plotting multiple files, the first column needs to be the same kind, such as `datetime`.
* Use the first column as X-values.
* Use the other columns as Y-values.
* (Option) Change the type of X: time series (datetime or elapsed seconds) or simple scatter.
* (Option) Use 2 Y-axis to plot data in different units and scales simultaneously.

## How to use

### Prepare

Need `pandas` and `plotly`.

```console
$ python3 -m pip install pandas
$ python3 -m pip install plotly
```

### Help

```console
$ ./graph.py -h
```

### Examples

```console
$ ./graph.py sample/simple.csv --yaxis-title Value
```

```console
$ ./graph.py sample/resource.csv --yaxis-columns Memory --yaxis2-title "ProcessorTime(%)" --yaxis2-columns ProcessorTime
```

```console
$ ./graph.py sample/simple.csv sample/resource.csv --graph-title "Plot multiple files" --yaxis-columns Memory --yaxis2-title "Other values" --yaxis2-columns ProcessorTime Value1 Value2 Value3
```

```console
$ ./graph.py sample/not-timeseries.csv --not-timeseries --yaxis-title Value
```
