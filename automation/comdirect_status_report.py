"""Automation script to display charts and reports of the data collected and
stored in the Excel files in the `export` folder. The script will parse the
Excel data in the files.

This script is based on Dash and Plotly, and the execution will result into a
server which can be accessed by the addressed informed on the console, for
example: http://127.0.0.1:8050/

Only the files matching the pattern `Export_Comdirect_` are evaluated, so any
other files in the folder will be ignored.

"""
from datetime import datetime
from pathlib import Path
from dash import html
from dash import dcc
from dash import dash_table
from dash_table.Format import Format, Group, Prefix, Scheme, Symbol, Align, Sign
from PIL import ImageColor
import dash
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def create_page():
    """Make a Dash application for displaying the charts. Dash will
    automatically load the .css which are in the assets folder, so there is
    no need to pass them. For that, this method of calling the app is
    necessary: app = dash.Dash(__name__)

    """
    app = dash.Dash(__name__)

    darker_tint = 'rgba(40, 40, 40, 255)'
    dark_tint = 'rgba(50, 50, 50, 255)'
    middle_tint = 'rgba(70, 70, 70, 255)'
    light_tint = 'rgba(90, 90, 90, 255)'
    lighter_tint = 'rgba(150, 150, 150, 255)'
    lightest_tint = 'rgba(200, 200, 200, 255)'

    ### TABLES #################################################################

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
        dict(id="Date", name="Date"),
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
        dict(id="Date", name="Date"),
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

    # --------------------------------------------------------------------------
    #   CHART 1
    # --------------------------------------------------------------------------
    fig_aggregated_current_value = go.Figure()

    # --------------------------------------------------------------------------
    #   Add the filled area below the lines.
    # --------------------------------------------------------------------------
    fig_aggregated_current_value.add_trace(go.Scatter(
        name='Depot',
        x=df_aggregated["Date"],
        y=df_aggregated["Depot Aggregated Current Value"],
        stackgroup='one',
        mode="none",
        fillcolor=color_fill_depot,
        showlegend=True,
    ))

    fig_aggregated_current_value.add_trace(go.Scatter(
        name='Balance',
        x=df_balances["Date"],
        y=df_balances["Balance Value"],
        stackgroup='one',
        mode="none",
        fillcolor=color_fill_balance,
        showlegend=True,
    ))

    fig_aggregated_current_value.add_trace(go.Scatter(
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
        fig_aggregated_current_value.add_trace(go.Scatter(
            name='Historical depot',
            x=df_aggregated_history["Date"],
            y=df_aggregated_history["Value Depot"],
            stackgroup='one',
            mode="none",
            fillcolor=color_fill_depot_history,
            showlegend=False,
        ))

        fig_aggregated_current_value.add_trace(go.Scatter(
            name='Historical balance',
            x=df_aggregated_history["Date"],
            y=df_aggregated_history["Value Account"],
            stackgroup='one',
            mode="none",
            fillcolor=color_fill_balance_history,
            showlegend=False,
        ))

        fig_aggregated_current_value.add_trace(go.Scatter(
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

    fig_aggregated_current_value.update_layout(
        xaxis_title="Date",
        yaxis_title="Value (EUR)",
        # legend_title="Legend"
    )
    fig_aggregated_current_value.update_layout(layout_charts)

    # --------------------------------------------------------------------------
    #   CHART 2 -- Stacked individual tickers
    # --------------------------------------------------------------------------
    opacity_elements = 0.6
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

    color_sequence_rgba = []
    for color in color_sequence:
        color_rgba = (*ImageColor.getcolor(color, "RGB"), opacity_elements)
        color_rgba = f"rgba{color_rgba}"
        color_sequence_rgba.append(color_rgba)

    fig_depots_current_value = go.Figure()

    i = 0
    for wkn in sorted(df_depots["WKN"].unique()):
        fig_depots_current_value.add_trace(go.Scatter(
            name=wkn,
            x=df_depots[df_depots["WKN"] == wkn]["Date"],
            y=df_depots[df_depots["WKN"] == wkn]["Current Value"],
            stackgroup='one',
            text=f"WKN: {wkn}",
            line=dict(color=middle_tint,
                      width=1.5),
            # mode="none",
            fillcolor=color_sequence_rgba[i],
            showlegend=True,
        ))
        i = i + 1

    fig_depots_current_value.update_layout(
        xaxis_title="Date",
        yaxis_title="Value (EUR)",
        # legend_title="Legend"
    )
    fig_depots_current_value.update_layout(layout_charts)

    # --------------------------------------------------------------------------
    #   CHART 3 -- Relative gain individual tickers
    # --------------------------------------------------------------------------
    opacity_elements = 1
    color_sequence_rgba = []
    for color in color_sequence:
        color_rgba = (*ImageColor.getcolor(color, "RGB"), opacity_elements)
        color_rgba = f"rgba{color_rgba}"
        color_sequence_rgba.append(color_rgba)

    fig_depots_current_value_line = go.Figure()

    i = 0
    for wkn in sorted(df_depots["WKN"].unique()):
        fig_depots_current_value_line.add_trace(go.Scatter(
            name=wkn,
            x=df_depots[df_depots["WKN"] == wkn]["Date"],
            y=df_depots[df_depots["WKN"] ==
                        wkn]["Profit/Loss Purchase Relative"],
            # stackgroup='one',
            text=f"WKN: {wkn}",
            line=dict(color=color_sequence_rgba[i],
                      width=2.5),
            mode="lines",
            fillcolor=color_sequence_rgba[i],
            showlegend=True,
        ))
        i = i + 1

    fig_depots_current_value_line.update_layout(
        xaxis_title="Date",
        yaxis_title="Value (EUR)",
        # legend_title="Legend"
    )
    fig_depots_current_value_line.update_layout(layout_charts)

    app.layout = html.Div(
        children=[
            html.H1(children='Results'),
            ################ CHART 1 ###########################################
            html.Div(
                [
                    html.H3(children='Total account balance'),
                    dcc.Graph(
                        id='fig_aggregated_current_value',
                        figure=fig_aggregated_current_value
                    )
                ]
            ),
            ################ CHART 2 ###########################################
            html.Div(
                [
                    html.H3(children='Depots current values'),
                    dcc.Graph(
                        id='fig_depots_current_value',
                        figure=fig_depots_current_value
                    )
                ]
            ),
            ################ CHART 3 ###########################################
            html.Div(
                [
                    html.H3(children='Split depots current values'),
                    dcc.Graph(
                        id='fig_depots_current_value_line',
                        figure=fig_depots_current_value_line
                    )
                ]
            ),
            ################ TABLE 1 ###########################################
            html.Div(
                [
                    html.H3(children='Aggregated values'),
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
                    html.H3(children='Depots values: ' + today_string),
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
                    html.H3(children='Depots values: Complete series'),
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

    return app


if __name__ == "__main__":

    folder = Path.cwd().resolve() / "export"

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

    # --------------------------------------------------------------------------
    #   Get all the files which contain data to be displayed. The files must be
    #   all in the "export" folder, and named with the pattern
    #   "Export_Comdirect_" to be included in the analysis.
    # --------------------------------------------------------------------------
    files = list(filter(Path.is_file, folder.glob('**/Export_Comdirect_*')))

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

    today_string = datetime.today().strftime('%Y-%m-%d')
    today_np = pd.to_datetime(today_string, format='%Y-%m-%d')
    df_depots_today = df_depots[df_depots['Date'] == today_string]

    df_aggregated["Date"] = pd.to_datetime(
        df_aggregated["Date"], format="%Y-%m-%d")
    df_aggregated["Date"] = df_aggregated["Date"].dt.date

    df_balances["Date"] = pd.to_datetime(
        df_balances["Date"], format="%Y-%m-%d")
    df_balances["Date"] = df_balances["Date"].dt.date

    # print(df_depots)
    # print(df_depots.columns)

    # # df_depots['Cumulative Profit/Loss Purchase Relative'] =
    df_depots['Delta Profit/Loss Purchase Relative'] = df_depots.sort_values(by=['Date', "WKN"]).groupby(
        ['Depot ID', 'WKN'])['Profit/Loss Purchase Relative'].diff()  # cumsum()  # ['Profit/Loss Purchase Relative'].rolling(2).sum().fillna(0)  # diff()  # .fillna(0)

    # print(df_cumulative.head(500))

    # print(df_depots['Cumulative Profit/Loss Purchase Relative'])

    app = create_page()

    app.run_server()
