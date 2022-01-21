"""Automation script to present the data collected from Comdirect. The data
used are the Excel files stored in the `export` folder. To keep compatibility
with older data stored, historical data stored in a CSV file, in the same folder
and named `History_Aggregated.csv`, will also be parsed and used. For the former
part, only the files matching the pattern `Export_Comdirect_` are evaluated,
so any other files in the folder will be ignored.

The script has an approach of parsing the data supplied and aggregate them,
forming longer and multiple dataframes.

The end goal is to summarize the data in the dashboard by using charts or
tables, to best present the information. The elements composing the page are:

1. Chart with the complete aggregated from the account.
2. Chart with split current values for all the depots.
3. Chart with relative gains/loses for each depot, based on a starting point
   in time, to which the value is zeroed and calculated relative to it. For
   this chart, a dropdown menu is available, so the user can select the
   timespam for analysis.
4. Table with the complete aggregated from the account.
5. Table with split current values for all the depots for the current day.
6. Table with split current values for all the depots.

This script is based on Dash and Plotly, and the execution will result into a
server which can be accessed by the addressed informed on the console, for
example: http://127.0.0.1:8050/

"""
from datetime import datetime
from pathlib import Path
from dash import html
from dash import dcc
from dash import dash_table
from dash.dependencies import Input, Output
from dash.dash_table.Format import Format, Group, Prefix, Scheme, Symbol, Align, Sign
from PIL import ImageColor
import dash
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.lib.config import Config


def create_chart_account_aggregated_values():
    """Create a chart with all the account aggregated values. If the dataframe
    for the historical data is available (different from ``None``) it will also
    be plotted, otherwise it is not included.

    Parameters
    ----------
        None
            This method uses data available from the script, created outside the
            method.

    Returns
    -------
        figure: `Plotly Graph Object`
            Resulting graph with data and configuration.

    """

    figure = go.Figure()

    # --------------------------------------------------------------------------
    #   Add the filled area below the lines.
    # --------------------------------------------------------------------------
    figure.add_trace(go.Scatter(
        name='Depot',
        x=df_aggregated["Date"],
        y=df_aggregated["Depot Aggregated Current Value"],
        stackgroup='one',
        mode="none",
        fillcolor=color_fill_depot,
        showlegend=True,
    ))

    figure.add_trace(go.Scatter(
        name='Balance',
        x=df_balances["Date"],
        y=df_balances["Balance Value"],
        stackgroup='one',
        mode="none",
        fillcolor=color_fill_balance,
        showlegend=True,
    ))

    figure.add_trace(go.Scatter(
        x=df_aggregated["Date"],
        y=df_aggregated["Account Total Value"],
        name='Total',
        mode="lines",
        showlegend=True,
        line=dict(color=color_line_total,
                  width=line_width),
        marker=dict(size=marker_size,
                    color=color_line_total_marker,
                    line=dict(width=line_width,
                              color=color_line_total))
    ))

    # --------------------------------------------------------------------------
    #   Add the filled area below the lines for the historical data. The line
    #   is the last one added, so it stays on top of the others.
    # --------------------------------------------------------------------------
    if df_aggregated_history is not None:
        figure.add_trace(go.Scatter(
            name='Historical depot',
            x=df_aggregated_history["Date"],
            y=df_aggregated_history["Value Depot"],
            stackgroup='one',
            mode="none",
            fillcolor=color_fill_depot_history,
            showlegend=False,
        ))

        figure.add_trace(go.Scatter(
            name='Historical balance',
            x=df_aggregated_history["Date"],
            y=df_aggregated_history["Value Account"],
            stackgroup='one',
            mode="none",
            fillcolor=color_fill_balance_history,
            showlegend=False,
        ))

        figure.add_trace(go.Scatter(
            x=df_aggregated_history["Date"],
            y=df_aggregated_history["Account Total Value"],
            name='Historical total',
            mode="lines",
            showlegend=False,
            line=dict(color=color_line_total_history,
                      width=line_width),
            marker=dict(size=marker_size,
                        color=color_line_total_history_marker,
                        line=dict(width=line_width,
                                  color=color_line_total_history))
        ))

    figure.update_layout(
        xaxis_title="Date",
        yaxis_title="Value (EUR)",
        # legend_title="Legend"
    )
    figure.update_layout(layout_charts)

    return figure


def create_line_chart(dataframe: pd.DataFrame,
                      group_by: str,
                      x_column: str,
                      y_column: str,
                      color_lines: list,
                      color_fills: list,
                      opacity_lines: float,
                      opacity_fills: float,
                      line_width: float,
                      x_label: str,
                      y_label: str,
                      stack_group: str = None):
    """Create a line chart.

    Parameters
    ----------
        dataframe: `Pandas Dataframe`
            Dataframe with the data to be plotted.
        group_by: `str`
            Name of the column in the Dataframe to be used a grouper.
        x_column: `str`
            Name of the column in the Dataframe to be used as X data.
        y_column: `str`
            Name of the column in the Dataframe to be used as Y data.
        color_lines: `List of str`
            List of strings with the hex values represening the colors to be
            used in sequence for the lines. Each color need to represented by a
            hash symbol (#) followed by 3 pairs of characters, to represent the
            RGB information.
        color_fills: `List of str`
            List of strings with the hex values represening the colors to be
            used in sequence for the fills. Each color need to represented by a
            hash symbol (#) followed by 3 pairs of characters, to represent the
            RGB information.
        opacity_lines: `float`
            Value between 0 and 1 to define the opacity of the colors for the
            lines. This is the alpha channel. A value of 0 means full
            transparency, while the value 1 means full opaque.
        opacity_fills: `float`
            Value between 0 and 1 to define the opacity of the colors for the
            fills. This is the alpha channel. A value of 0 means full
            transparency, while the value 1 means full opaque.
        line_width: `float`
            Width of the lines in plot.
        x_label: `str`
            String with the name of label to be used as the title for the X
            axis.
        y_label: `str`
            String with the name of label to be used as the title for the Y
            axis.
        stack_group: `str`, optional
            Name of the group to stack the plots. If no stacking is desired,
            value ```None`` need to be assigned.

    Returns
    -------
        figure: `Plotly Graph Object`
            Resulting graph with data and configuration.

    """
    color_lines_rgba = convert_hex_to_rgba(color_sequence=color_lines,
                                           opacity=opacity_lines)

    color_fills_rgba = convert_hex_to_rgba(color_sequence=color_fills,
                                           opacity=opacity_fills)

    figure = go.Figure()

    i = 0
    for element in sorted(dataframe[group_by].unique()):
        figure.add_trace(go.Scatter(
            name=element,
            x=dataframe[dataframe[group_by] == element][x_column],
            y=dataframe[dataframe[group_by] == element][y_column],
            stackgroup=stack_group,
            text=f"{group_by}: {element}",
            line=dict(color=color_lines_rgba[i % len(color_lines_rgba)],
                      width=line_width),
            mode="lines",
            fillcolor=color_fills_rgba[i % len(color_fills_rgba)],
            showlegend=True,
        ))
        i = i + 1

    figure.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        # legend_title="Legend"
    )
    figure.update_layout(layout_charts)

    return figure


def convert_hex_to_rgba(color_sequence: list, opacity: float):
    """Converts a list of Hex based values to a RGBA equivalent list. The alpha
    channel component is provenient from the ``opacity`` input.
    """

    if isinstance(color_sequence, str):
        color_sequence = [color_sequence]

    color_sequence_rgba = []
    for color in color_sequence:
        color_rgba = (*ImageColor.getcolor(color, "RGB"), opacity)
        color_rgba = f"rgba{color_rgba}"
        color_sequence_rgba.append(color_rgba)

    return color_sequence_rgba


def define_timespam(timespam: str):
    """Converts a string input with a timespam and returns the start date from
    today.
    """
    if timespam == "all":
        timespam_date = np.datetime64('today') - np.timedelta64(9999, 'D')
    elif timespam == "l1d":
        timespam_date = np.datetime64('today') - np.timedelta64(1, 'D')
    elif timespam == "l3d":
        timespam_date = np.datetime64('today') - np.timedelta64(3, 'D')
    elif timespam == "l7d":
        timespam_date = np.datetime64('today') - np.timedelta64(7, 'D')
    elif timespam == "l15d":
        timespam_date = np.datetime64('today') - np.timedelta64(15, 'D')
    elif timespam == "l30d":
        timespam_date = np.datetime64('today') - np.timedelta64(30, 'D')
    elif timespam == "l60d":
        timespam_date = np.datetime64('today') - np.timedelta64(60, 'D')
    elif timespam == "l90d":
        timespam_date = np.datetime64('today') - np.timedelta64(90, 'D')
    elif timespam == "l180d":
        timespam_date = np.datetime64('today') - np.timedelta64(180, 'D')
    elif timespam == "l360d":
        timespam_date = np.datetime64('today') - np.timedelta64(360, 'D')

    return timespam_date


def create_filtered_depots_dataframe(timespam: str):
    """Creates the percentual incremental dataframe. This dataframe will start
    each signal from 0 value (gain/loss) and then produce incremental steps
    based on the daily gain or loss.

    This method is used a callback since it needs to be called for the dropdown
    menu in the Dash dashboard. 

    The operation takes a few steps:

    1. Copy of the Depot dataframe
    2. Cut-off (filter out) data before a desidered target. This step is
       important, since the data will be displayed in reference to the new
       start.
    3. Add a new row to cover for cases when the first invesrtiment comes
       after the cut-off date, otherwise they will have an offset in the
       operation due to losing the first entry.
    4. Builds up the list of changes to add to the dataframe.

    """

    timespam_date = define_timespam(timespam=timespam)

    df_depots_filter = df_depots.copy()

    cut_np = pd.to_datetime(str(timespam_date), format='%Y-%m-%d')
    df_depots_filter = df_depots_filter[~(df_depots_filter['Date'] < cut_np)]

    earlist_date = df_depots_filter["Date"].min()

    df_depots_filter.sort_values(
        by=["WKN", "Date"], ignore_index=True, inplace=True)

    # --------------------------------------------------------------------------
    #   This step will add a new row with zeros to each WKN. The new row is
    #   assigned to the previous day of the first entry. This is due to make
    #   smooth start when the WKN starts after the first date of the filter.
    #   After adding the new rows, then re-sort the dataframe.
    # --------------------------------------------------------------------------
    new_wkn = ""
    for index, row in df_depots_filter.iterrows():
        if row["WKN"] != new_wkn and row["Date"] > earlist_date:
            new_row = row
            new_row["Date"] = row["Date"] - np.timedelta64(1, 'D')
            new_row["Quantity"] = 0
            new_row["Available Quantity"] = 0
            new_row["Purchase Value"] = 0
            new_row["Purchase Price"] = 0
            new_row["Current Value"] = 0
            new_row["Current Price"] = 0
            new_row["Profit/Loss Purchase Absolute Value"] = 0
            new_row["Profit/Loss Purchase Relative"] = 0
            new_row["Profit/Loss Previous Day Absolute Value"] = 0
            new_row["Profit/Loss Previous Day Relative"] = 0
            df_depots_filter = df_depots_filter.append(
                new_row, ignore_index=True)
        new_wkn = row["WKN"]

    df_depots_filter.sort_values(
        by=["WKN", "Date"], ignore_index=True, inplace=True)

    # --------------------------------------------------------------------------
    #   This step will add a new row with zeros to each WKN. The new row is
    #   assigned to the previous day of the first entry. This is due to make
    #   smooth start when the WKN starts after the first date of the filter.
    # --------------------------------------------------------------------------
    list_new_delta = []
    list_new_delta_sum = []
    new_wkn = ""
    new_delta = 0
    delta_sum = 0
    for index, row in df_depots_filter.iterrows():
        if row["WKN"] != new_wkn:
            value_shift = row["Profit/Loss Purchase Relative"]
            value_relative_new = 0
            value_relative_old = 0
            new_delta = 0
            delta_sum = 0

        new_wkn = row["WKN"]
        value_relative_new = row["Profit/Loss Purchase Relative"] - value_shift
        new_delta = value_relative_new - value_relative_old
        delta_sum = delta_sum + new_delta

        list_new_delta.append(new_delta)
        list_new_delta_sum.append(delta_sum)

        value_relative_old = value_relative_new

    df_depots_filter["Delta Profit/Loss Purchase Relative"] = list_new_delta
    df_depots_filter["Cumulative Delta Profit/Loss Purchase Relative"] = list_new_delta_sum

    return df_depots_filter


def create_historical_aggregated_dataframe(folder: Path):
    # --------------------------------------------------------------------------
    #   Loads first any historical data which was stored before the scripts /
    #   project to be available. For the historical data, information is
    #   expected as a .csv file. Only the aggregated value of the account is
    #   supported for it. The cav file must be named "History_Aggregated" and
    #   also be located in the "Export" folder.
    # --------------------------------------------------------------------------
    historical_file = folder / "History_Aggregated.csv"
    if historical_file.is_file():
        df_aggregated_history = pd.read_csv(historical_file,
                                            header=0,
                                            quotechar='"',
                                            skipinitialspace=True,
                                            decimal=",",
                                            delimiter=';',
                                            thousands='.',
                                            parse_dates=[1],
                                            )

        df_aggregated_history["Date"] = pd.to_datetime(
            df_aggregated_history["Date"], format="%d-%m-%Y")
        df_aggregated_history["Date"] = df_aggregated_history["Date"].dt.date

        df_aggregated_history["Account Total Value"] = df_aggregated_history["Value Depot"] + \
            df_aggregated_history["Value Account"]

        df_aggregated_history["Account Total Value Unit"] = "EUR"

        # df_aggregated_history.drop(columns=["Value Depot", "Value Account"],
        #                            inplace=True)

        df_aggregated_history.rename(
            columns={
                "Depot ID": "Depot Aggregated ID",
                "Unit": "Depot Aggregated Current Value Unit"
            },
            inplace=True
        )

        if 'Depot Aggregated Purchase Value' not in df_aggregated_history.columns:
            df_aggregated_history['Depot Aggregated Purchase Value'] = np.nan

        if 'Depot Aggregated Purchase Value Unit' not in df_aggregated_history.columns:
            df_aggregated_history['Depot Aggregated Purchase Value Unit'] = "EUR"

        if 'Depot Aggregated Current Value' not in df_aggregated_history.columns:
            df_aggregated_history['Depot Aggregated Current Value'] = np.nan

        if 'Depot Aggregated Current Value Unit' not in df_aggregated_history.columns:
            df_aggregated_history['Depot Aggregated Current Value Unit'] = "EUR"

        if 'Depot Aggregated Profit/Loss Purchase Absolute Value' not in df_aggregated_history.columns:
            df_aggregated_history['Depot Aggregated Profit/Loss Purchase Absolute Value'] = np.nan

        if 'Depot Aggregated Profit/Loss Purchase Absolute Unit' not in df_aggregated_history.columns:
            df_aggregated_history['Depot Aggregated Profit/Loss Purchase Absolute Unit'] = "EUR"

        if 'Depot Aggregated Profit/Loss Purchase Relative' not in df_aggregated_history.columns:
            df_aggregated_history['Depot Aggregated Profit/Loss Purchase Relative'] = np.nan

        if 'Depot Aggregated Profit/Loss Previous Day Absolute Value' not in df_aggregated_history.columns:
            df_aggregated_history['Depot Aggregated Profit/Loss Previous Day Absolute Value'] = np.nan

        if 'Depot Aggregated Profit/Loss Previous Day Absolute Unit' not in df_aggregated_history.columns:
            df_aggregated_history['Depot Aggregated Profit/Loss Previous Day Absolute Unit'] = "EUR"

        if 'Depot Aggregated Profit/Loss Previous Day Relative' not in df_aggregated_history.columns:
            df_aggregated_history['Depot Aggregated Profit/Loss Previous Day Relative'] = np.nan

    else:
        df_aggregated_history = None

    return df_aggregated_history


def create_combined_dataframes(folder: Path, date_today: str):
    # --------------------------------------------------------------------------
    #   Get all the files which contain data to be displayed. The files must be
    #   all in the "export" folder, and named with the pattern
    #   "Export_Comdirect_" to be included in the analysis.
    # --------------------------------------------------------------------------
    files = list(filter(Path.is_file, folder.glob('**/Export_Comdirect_*')))
    if len(files) < 1:
        return None, None, None, None

    df_depots = pd.DataFrame()
    df_balances = pd.DataFrame()
    df_aggregated = pd.DataFrame()

    df_file_aggregated = pd.read_excel(
        files[0], sheet_name="Depot Positions Aggregated")

    i = 0
    for file in files:

        df_file_aggregated = pd.read_excel(
            file, sheet_name="Depot Positions Aggregated")
        df_file_balance = pd.read_excel(
            file, sheet_name="Balance")
        df_file_depots = pd.read_excel(
            file, sheet_name="Depot Positions")

        df_file_aggregated["Account Total Value"] = df_file_aggregated["Depot Aggregated Current Value"] + \
            df_file_balance["Balance Value"].iloc[-1]
        df_file_aggregated["Account Total Value Unit"] = "EUR"

        if i == 0:
            df_aggregated = df_file_aggregated
            df_balances = df_file_balance
            df_depots = df_file_depots
        else:
            df_aggregated = df_aggregated.append(df_file_aggregated)
            df_balances = df_balances.append(df_file_balance)
            df_depots = df_depots.append(df_file_depots)

        i = i + 1

    today_np = pd.to_datetime(date_today, format='%Y-%m-%d')
    df_depots_today = df_depots[df_depots['Date'] == today_string]

    # --------------------------------------------------------------------------
    #   Redefine the dates from string as datetime (day only) format.
    # --------------------------------------------------------------------------
    df_aggregated["Date"] = pd.to_datetime(
        df_aggregated["Date"], format="%Y-%m-%d", infer_datetime_format=True)
    df_aggregated["Date"] = df_aggregated["Date"].dt.date

    df_balances["Date"] = pd.to_datetime(
        df_balances["Date"], format="%Y-%m-%d", infer_datetime_format=True)
    df_balances["Date"] = df_balances["Date"].dt.date

    df_depots["Date"] = pd.to_datetime(
        df_depots["Date"], format="%Y-%m-%d", infer_datetime_format=True)
    df_depots["Date"] = df_depots["Date"].dt.date

    df_depots_today.loc[:, 'Date'] = pd.to_datetime(
        df_depots_today['Date'], format="%Y-%m-%d", infer_datetime_format=True)
    df_depots_today.loc[:, 'Date'] = df_depots_today["Date"].dt.date

    df_aggregated['Date'] = pd.to_datetime(
        df_aggregated['Date'], infer_datetime_format=True)
    df_balances['Date'] = pd.to_datetime(
        df_balances['Date'], infer_datetime_format=True)
    df_depots['Date'] = pd.to_datetime(
        df_depots['Date'], infer_datetime_format=True)
    df_depots_today.loc[:, 'Date'] = pd.to_datetime(
        df_depots_today['Date'], infer_datetime_format=True)

    # --------------------------------------------------------------------------
    #   Reestructure of the indexes, so they are all incrementing for the
    #   complete list. Without this operation, the indexes are repeatition
    #   from the previous part of the dataframes. Also eliminates unecessary
    #   columns.
    # --------------------------------------------------------------------------
    df_aggregated.drop(columns=["Unnamed: 0"], inplace=True)
    df_aggregated.index = pd.RangeIndex(len(df_aggregated.index))
    df_aggregated.reset_index(inplace=True, drop=True)

    df_balances.drop(columns=["Unnamed: 0"], inplace=True)
    df_balances.index = pd.RangeIndex(len(df_balances.index))
    df_balances.reset_index(inplace=True, drop=True)

    df_depots.drop(columns=["Unnamed: 0"], inplace=True)
    df_depots.index = pd.RangeIndex(len(df_depots.index))
    df_depots.reset_index(inplace=True, drop=True)

    df_depots.sort_values(
        by=["WKN", "Date"], ignore_index=True, inplace=True)

    return df_depots, df_balances, df_aggregated, df_depots_today

################################################################################
#   Main application
################################################################################


LOGGER_NAME = "invst.comdirect_status_report"


today_string = datetime.today().strftime('%Y-%m-%d')

# --------------------------------------------------------------------------
#   Defines the location of the files with configurations and load them.
# --------------------------------------------------------------------------
config_base_path = Path.cwd().resolve() / "cfg"
config_access_file = config_base_path / "api-cfg.json"
config_access_userdata_file = config_base_path / "user" / "api-cfg-access.json"
config_local_file = config_base_path / "local" / "local.json"
config_parameters_file = config_base_path / "parameters.json"

config = Config(logger_name=LOGGER_NAME)
config.load_config(filename=config_access_file)
config.load_config(filename=config_access_userdata_file)
config.load_config(filename=config_local_file)
folder = Path(config.local_config["paths"]["data_storage"])
# folder = Path.cwd().resolve() / "export"

df_aggregated_history = create_historical_aggregated_dataframe(
    folder=folder)

(df_depots,
    df_balances,
    df_aggregated,
    df_depots_today) = create_combined_dataframes(folder=folder,
                                                  date_today=today_string)

# ------------------------------------------------------------------------------
#   Configuration definitions: Colors
# ------------------------------------------------------------------------------

darker_tint = 'rgba(40, 40, 40, 255)'
dark_tint = 'rgba(50, 50, 50, 255)'
middle_tint = 'rgba(70, 70, 70, 255)'
light_tint = 'rgba(90, 90, 90, 255)'
lighter_tint = 'rgba(150, 150, 150, 255)'
lightest_tint = 'rgba(200, 200, 200, 255)'

color_sequence = [
    "#E26A2C",
    "#FF8243",
    "#FDA65D",
    "#FFD07F",
    "#fdfa66",
    "#E6DD3B",
    "#29BB89",
    "#289672",
    "#1E6F5C",
    "#132743",
    "#2F86A6",
    "#009DAE",
    "#71DFE7",
    "#FCDADA",
    "#FFA5A5",
    "#E5707E",
    "#EF4F4F",
]

### TABLES #####################################################################

date_format = Format(
    sign=Sign.parantheses,
    group=True,
    precision=2,
    scheme=Scheme.fixed,
    symbol=Symbol.yes,
    symbol_suffix=' €',
    group_delimiter='.',
    decimal_delimiter=',',
    align=Align.right
)

money_format = Format(
    sign=Sign.parantheses,
    group=True,
    precision=2,
    scheme=Scheme.fixed,
    symbol=Symbol.yes,
    symbol_suffix=' €',
    group_delimiter='.',
    decimal_delimiter=',',
    align=Align.right
)

percentage_format = Format(
    sign=Sign.parantheses,
    group=True,
    precision=2,
    scheme=Scheme.fixed,
    symbol=Symbol.yes,
    symbol_suffix=' %',
    group_delimiter='.',
    decimal_delimiter=',',
    align=Align.right
)

columns_aggregated = [
    dict(id="Date", name="Date",
            type='datetime',
            format="%Y"),
    dict(id="Depot Aggregated ID", name="Depot ID"),
    dict(id="Depot Aggregated Purchase Value", name="Purchase Value",
            type='numeric',
            format=money_format),
    dict(id="Depot Aggregated Current Value", name="Current Value",
            type='numeric',
            format=money_format),
    dict(id="Depot Aggregated Profit/Loss Purchase Absolute Value",
            name="Profit/Loss from Purchase Absolute Value",
            type='numeric',
            format=money_format),
    dict(id="Depot Aggregated Profit/Loss Purchase Relative",
            name="Profit/Loss from Purchase Relative",
            type='numeric',
            format=percentage_format),
    dict(id="Depot Aggregated Profit/Loss Previous Day Absolute Value",
            name="Profit/Loss from Previous Day Absolute Value",
            type='numeric',
            format=money_format),
    dict(id="Depot Aggregated Profit/Loss Previous Day Relative",
            name="Profit/Loss from Previous Day Relative",
            type='numeric',
            format=percentage_format)
]

columns_depots = [
    dict(id="Date", name="Date",
            type='datetime'),
    dict(id="WKN", name="WKN"),
    dict(id="Quantity", name="Quantity",
            type='numeric'),
    dict(id="Available Quantity", name="Available Quantity",
            type='numeric'),
    dict(id="Hedgeability", name="Hedgeability"),
    dict(id="Purchase Price", name="Purchase Price",
            type='numeric',
            format=money_format),
    dict(id="Current Price", name="Current Price",
            type='numeric',
            format=money_format),
    dict(id="Purchase Value", name="Purchase Value",
            type='numeric',
            format=money_format),
    dict(id="Current Value", name="Current Value",
            type='numeric',
            format=money_format),
    dict(id="Profit/Loss Purchase Absolute Value",
            name="Profit/Loss from Purchase Absolute Value",
            type='numeric',
            format=money_format),
    dict(id="Profit/Loss Purchase Relative",
            name="Profit/Loss from Purchase Relative",
            type='numeric',
            format=percentage_format),
    dict(id="Profit/Loss Previous Day Absolute Value",
            name="Profit/Loss from Previous Day Absolute Value",
            type='numeric',
            format=money_format),
    dict(id="Profit/Loss Previous Day Relative",
            name="Profit/Loss from Previous Day Relative",
            type='numeric',
            format=percentage_format)
]

conditional_cell_aggregated = [
    {
        'if':
        {
            'column_id': 'Date',
        },
        'textAlign': 'center'
    },
    {
        'if':
        {
            'column_id': 'Depot Aggregated ID',
        },
        'textAlign': 'center'
    },
    {
        'if':
        {
            'column_id': 'Depot Aggregated ID',
        },
        'width': '330px'
    },
]

conditional_cell_depots = [
    {
        'if':
        {
            'column_id': 'Date',
        },
        'textAlign': 'center'
    },
    {
        'if':
        {
            'column_id': 'WKN',
        },
        'textAlign': 'center'
    },
    {
        'if':
        {
            'column_id': 'Quantity',
        },
        'textAlign': 'center'
    },
    {
        'if':
        {
            'column_id': 'Available Quantity',
        },
        'textAlign': 'center'
    },
    {
        'if':
        {
            'column_id': 'Hedgeability',
        },
        'textAlign': 'center'
    },
]

conditional_data_aggregated = [
    {
        'if':
        {
            'filter_query': '{Depot Aggregated Profit/Loss Purchase Absolute Value} < 0',
            'column_id': 'Depot Aggregated Profit/Loss Purchase Absolute Value'
        },
        'background-color': 'tomato',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Depot Aggregated Profit/Loss Purchase Absolute Value} > 0',
            'column_id': 'Depot Aggregated Profit/Loss Purchase Absolute Value'
        },
        'background-color': 'green',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Depot Aggregated Profit/Loss Purchase Relative} < 0',
            'column_id': 'Depot Aggregated Profit/Loss Purchase Relative'
        },
        'background-color': 'tomato',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Depot Aggregated Profit/Loss Purchase Relative} > 0',
            'column_id': 'Depot Aggregated Profit/Loss Purchase Relative'
        },
        'background-color': 'green',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Depot Aggregated Profit/Loss Previous Day Absolute Value} < 0',
            'column_id': 'Depot Aggregated Profit/Loss Previous Day Absolute Value'
        },
        'background-color': 'tomato',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Depot Aggregated Profit/Loss Previous Day Absolute Value} > 0',
            'column_id': 'Depot Aggregated Profit/Loss Previous Day Absolute Value'
        },
        'background-color': 'green',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Depot Aggregated Profit/Loss Previous Day Relative} < 0',
            'column_id': 'Depot Aggregated Profit/Loss Previous Day Relative'
        },
        'background-color': 'tomato',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Depot Aggregated Profit/Loss Previous Day Relative} > 0',
            'column_id': 'Depot Aggregated Profit/Loss Previous Day Relative'
        },
        'background-color': 'green',
        'color': 'white'
    },
]

conditional_data_depots = [
    {
        'if':
        {
            'filter_query': '{Profit/Loss Purchase Absolute Value} < 0',
            'column_id': 'Profit/Loss Purchase Absolute Value'
        },
        'background-color': 'tomato',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Profit/Loss Purchase Absolute Value} > 0',
            'column_id': 'Profit/Loss Purchase Absolute Value'
        },
        'background-color': 'green',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Profit/Loss Purchase Relative} < 0',
            'column_id': 'Profit/Loss Purchase Relative'
        },
        'background-color': 'tomato',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Profit/Loss Purchase Relative} > 0',
            'column_id': 'Profit/Loss Purchase Relative'
        },
        'background-color': 'green',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Profit/Loss Previous Day Absolute Value} < 0',
            'column_id': 'Profit/Loss Previous Day Absolute Value'
        },
        'background-color': 'tomato',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Profit/Loss Previous Day Absolute Value} > 0',
            'column_id': 'Profit/Loss Previous Day Absolute Value'
        },
        'background-color': 'green',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Profit/Loss Previous Day Relative} < 0',
            'column_id': 'Profit/Loss Previous Day Relative'
        },
        'background-color': 'tomato',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Profit/Loss Previous Day Relative} > 0',
            'column_id': 'Profit/Loss Previous Day Relative'
        },
        'background-color': 'green',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Hedgeability} = "HEDGED"',
            'column_id': 'Hedgeability'
        },
        'background-color': 'green',
        'color': 'white'
    },
    {
        'if':
        {
            'filter_query': '{Hedgeability} = "HEDGEABLE"',
            'column_id': 'Hedgeability'
        },
        'background-color': 'tomato',
        'color': 'white'
    }
]

table_style_cell = dict(
    minWidth='50px',
    width='50px',
    maxWidth='100px',
    # textAlign='left',
    whiteSpace='normal')

table_style_header = dict(
    backgroundColor=darker_tint,
    color=lighter_tint,
    border='1px solid ' + light_tint,
    textAlign='center',
    fontWeight='bold',
    whiteSpace="normal",
    height="auto")

table_style_data = dict(
    backgroundColor=middle_tint,
    border='1px solid ' + light_tint,
    color=lightest_tint,)

### CHARTS #################################################################

marker_size = 1
line_width = 4
color_line_total = "#FFBD35"
color_line_total_marker = color_line_total
color_line_total_history = color_line_total
color_line_total_history_marker = color_line_total_history

opacity_area = 0.5
color_fill_depot = f"rgba(0,217,126,{opacity_area})"
color_fill_balance = f"rgba(0,242,141,{opacity_area})"
color_fill_depot_history = color_fill_depot
color_fill_balance_history = color_fill_balance

layout_charts = go.Layout(
    autosize=True,
    height=600,
    margin=dict(l=100, r=200, b=60, t=40, pad=4),
    plot_bgcolor=middle_tint,
    paper_bgcolor=dark_tint,
    xaxis={'automargin': True,
           'gridcolor': light_tint,
           'gridwidth': 2,
           'linecolor': lighter_tint,
           'ticks': '',
           'title': {'standoff': 15},
           'zerolinecolor': lighter_tint,
           'zerolinewidth': 2,
           'tickfont': {
               'color': lightest_tint
           },
           'title': {
               'font': {
                   'color': lightest_tint
               }
           }
           },
    yaxis={'automargin': True,
           'gridcolor': light_tint,
           'gridwidth': 2,
           'linecolor': lighter_tint,
           'ticks': '',
           'title': {'standoff': 15},
           'zerolinecolor': lighter_tint,
           'zerolinewidth': 2,
           'tickfont': {
               'color': lightest_tint
           },
           'title': {
               'font': {
                   'color': lightest_tint
               }
           }
           },
    legend={
        'bgcolor': middle_tint,
        'bordercolor': darker_tint,
        'borderwidth': 2,
        'font': {
            'color': lightest_tint
        }
    },
    # paper_bgcolor="LightSteelBlue"
)


def make_report(app):
    # ------------------------------------------------------------------------------
    #   Make a Dash application for displaying the charts. Dash will
    #   automatically load the .css which are in the assets folder, so there is
    #   no need to pass them. For that, this method of calling the app is
    #   necessary: app = dash.Dash(__name__)
    # ------------------------------------------------------------------------------
    # app = dash.Dash(__name__)

    if (df_depots is not None) and (df_balances is not None) and (df_aggregated is not None) and (df_depots_today is not None):

        fig_aggregated_current_value = \
            create_chart_account_aggregated_values()

        fig_depots_current_value = \
            create_line_chart(dataframe=df_depots,
                              group_by="WKN",
                              x_column="Date",
                              y_column="Current Value",
                              color_lines=middle_tint,
                              color_fills=color_sequence,
                              opacity_lines=1,
                              opacity_fills=0.6,
                              line_width=1.5,
                              x_label="Date",
                              y_label="Value (EUR)",
                              stack_group="one")

        # --------------------------------------------------------------------------
        #   Creation of the dashboard HTML.
        # --------------------------------------------------------------------------
        app.layout = html.Div(
            children=[
                html.H1(children='Results'),
                ################ CHART 1 ###########################################
                html.Div(
                    [
                        html.H3(children='Total account balance',
                                className="display_component_first"),
                        dcc.Graph(
                            id='fig_aggregated_current_value',
                            figure=fig_aggregated_current_value
                        )
                    ]
                ),
                ################ CHART 2 ###########################################
                html.Div(
                    [
                        html.H3(children='Depots current values',
                                className="display_component"),
                        dcc.Graph(
                            id='fig_depots_current_value',
                            figure=fig_depots_current_value
                        )
                    ]
                ),
                ################ CHART 3 ###########################################
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(children='Depots relative gain',
                                        className="display_component"),
                            ],
                            style={"width": "80%", 'display': 'inline-block'}
                        ),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id='timespam-relative-dropdown',
                                    options=[
                                        {'label': 'Last 1 day', 'value': 'l1d'},
                                        {'label': 'Last 3 days', 'value': 'l3d'},
                                        {'label': 'Last 7 days', 'value': 'l7d'},
                                        {'label': 'Last 15 days', 'value': 'l15d'},
                                        {'label': 'Last 30 days', 'value': 'l30d'},
                                        {'label': 'Last 60 days', 'value': 'l60d'},
                                        {'label': 'Last 90 days', 'value': 'l90d'},
                                        {'label': 'Last 180 days',
                                            'value': 'l180d'},
                                        {'label': 'Last 360 days',
                                            'value': 'l360d'},
                                        {'label': 'All time', 'value': 'all'},
                                    ],
                                    value='all'
                                ),
                            ],
                            style={"width": "20%", 'display': 'inline-block'}
                        ),
                        dcc.Graph(
                            # ------------------------------------------------------
                            #   A important note here is that this chart is updates
                            #   depending on the chosen value for the dropdown menu,
                            #   so updated by the callback function. The figure is
                            #   left open, diffent from the others.
                            # ------------------------------------------------------
                            id='fig_depots_relative_increment_value'
                        )
                    ]
                ),
                ################ TABLE 1 ###########################################
                html.Div(
                    [
                        html.H3(children='Aggregated values',
                                className="display_component"),
                        dash_table.DataTable(
                            id='table_aggregated',
                            filter_action='native',
                            sort_action='native',
                            # fixed_rows={'headers': True, 'data': 0},
                            page_size=20,
                            sort_mode='multi',
                            sort_by=[{'column_id': 'Date', 'direction': 'desc'},
                                     {'column_id': 'Depot Aggregated Profit/Loss Previous Day Absolute Value',
                                     'direction': 'desc'}],
                            columns=columns_aggregated,
                            data=df_aggregated.to_dict('records'),
                            style_cell=table_style_cell,
                            style_header=table_style_header,
                            style_data=table_style_data,
                            style_table={'overflowX': 'auto'},
                            style_cell_conditional=conditional_cell_aggregated,
                            style_data_conditional=conditional_data_aggregated,
                        )
                    ]
                ),
                ################ TABLE 2 ###########################################
                html.Div(
                    [
                        html.H3(children='Depots values: ' + today_string,
                                className="display_component"),
                        dash_table.DataTable(
                            id='table_depots',
                            filter_action='native',
                            sort_action='native',
                            # fixed_rows={'headers': True, 'data': 0},
                            page_size=20,
                            sort_mode='multi',
                            sort_by=[{'column_id': 'Date', 'direction': 'desc'},
                                     {'column_id': 'Profit/Loss Previous Day Absolute Value',
                                     'direction': 'desc'},
                                     {'column_id': 'WKN', 'direction': 'asc'}],
                            columns=columns_depots,
                            data=df_depots_today.to_dict('records'),
                            style_cell=table_style_cell,
                            style_header=table_style_header,
                            style_data=table_style_data,
                            style_table={'overflowX': 'auto'},
                            style_cell_conditional=conditional_cell_depots,
                            style_data_conditional=conditional_data_depots,
                        )
                    ]
                ),
                ################ TABLE 3 ###########################################
                html.Div(
                    [
                        html.H3(children='Depots values: Complete series',
                                className="display_component"),
                        dash_table.DataTable(
                            id='table_depots_all',
                            filter_action='native',
                            sort_action='native',
                            page_size=20,
                            sort_mode='multi',
                            sort_by=[{'column_id': 'Date', 'direction': 'desc'},
                                     {'column_id': 'Profit/Loss Previous Day Absolute Value',
                                     'direction': 'desc'},
                                     {'column_id': 'WKN', 'direction': 'asc'}],
                            columns=columns_depots,
                            data=df_depots.to_dict('records'),
                            style_cell=table_style_cell,
                            style_header=table_style_header,
                            style_data=table_style_data,
                            style_table={'overflowX': 'auto'},
                            style_cell_conditional=conditional_cell_depots,
                            style_data_conditional=conditional_data_depots,
                        )
                    ]
                )
                ################ END ###############################################
            ]
        )
    else:
        app.layout = html.Div("Report Dash Test")

    app.css.append_css({"external_url": f"/static/styles/layout.css"})


# @app.callback(
#     Output('fig_depots_relative_increment_value',
#            'figure'),
#     [Input('timespam-relative-dropdown', 'value')]
# )
# def update_output(value):

#     df_depots_filter = create_filtered_depots_dataframe(timespam=value)

#     figure = create_line_chart(dataframe=df_depots_filter,
#                                group_by="WKN",
#                                x_column="Date",
#                                y_column="Cumulative Delta Profit/Loss Purchase Relative",
#                                color_lines=color_sequence,
#                                color_fills=color_sequence,
#                                opacity_lines=1,
#                                opacity_fills=1,
#                                line_width=2.5,
#                                x_label="Date",
#                                y_label="Value (%)",
#                                stack_group=None)
#     return figure


if __name__ == "__main__":

    app.run_server()
