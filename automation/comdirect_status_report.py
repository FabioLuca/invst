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

    fig_aggregated_current_value = px.line(
        df_aggregated,
        x="Date",
        y="Account Total Value",
        markers=False)

    marker_size = 1
    line_width = 3
    color_line_actual = "#337d05"
    color_line_actual_marker = "#68ab3e"
    color_line_history = color_line_actual  # "#10946f"
    color_line_history_marker = color_line_actual_marker  # "#44cfa8"
    opacity_history = 0.8

    fig_aggregated_current_value.update_traces(
        line=dict(color=color_line_actual,
                  width=line_width),
        marker=dict(size=marker_size,
                    color=color_line_actual_marker,
                    line=dict(width=line_width,
                              color=color_line_actual)),
        # selector=dict(mode='markers')
    )

    if df_aggregated_history is not None:
        fig_aggregated_current_value.add_scatter(
            x=df_aggregated_history["Date"],
            y=df_aggregated_history["Account Total Value"],
            name='History',
            mode="lines",  # +markers",
            opacity=opacity_history,
            line=dict(color=color_line_history,
                      width=line_width),
            marker=dict(size=marker_size,
                        color=color_line_history_marker,
                        line=dict(width=line_width,
                                  color=color_line_history))
        )

    fig_aggregated_current_value.update_layout(
        xaxis_title="Date",
        yaxis_title="Value (EUR)",
        # legend_title="Legend"
    )
    fig_aggregated_current_value.update_layout(layout_charts)

    fig_depots_current_value = px.area(
        df_depots,
        x="Date",
        y="Current Value",
        # olor_discrete_sequence=px.colors.sequential.Rainbow,
        color="WKN")

    fig_depots_current_value.update_layout(
        xaxis_title="Date",
        yaxis_title="Value (EUR)",
        # legend_title="Legend"
    )
    fig_depots_current_value.update_layout(layout_charts)
    fig_depots_current_value.for_each_trace(
        lambda trace: trace.update(fillcolor=trace.line.color))

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
                    html.H3(children='Split depots current values'),
                    dcc.Graph(
                        id='fig_depots_current_value',
                        figure=fig_depots_current_value
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

        df_aggregated_history.drop(columns=["Value Depot", "Value Account"],
                                   inplace=True)

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
    df_aggregated = pd.DataFrame()

    df_file_aggregated = pd.read_excel(
        files[0], sheet_name="Depot Positions Aggregated")

    i = 0
    for file in files:

        df_file_aggregated = pd.read_excel(
            file, sheet_name="Depot Positions Aggregated")
        df_file_aggregated_balance = pd.read_excel(
            file, sheet_name="Balance")
        df_file_depots = pd.read_excel(
            file, sheet_name="Depot Positions")

        df_file_aggregated["Account Total Value"] = df_file_aggregated["Depot Aggregated Current Value"] + \
            df_file_aggregated_balance["Balance Value"].iloc[-1]
        df_file_aggregated["Account Total Value Unit"] = "EUR"

        if i == 0:
            df_aggregated = df_file_aggregated
            df_depots = df_file_depots
        else:
            df_aggregated = df_aggregated.append(df_file_aggregated)
            df_depots = df_depots.append(df_file_depots)

        i = i + 1

    today_string = datetime.today().strftime('%Y-%m-%d')
    today_np = pd.to_datetime(today_string, format='%Y-%m-%d')
    df_depots_today = df_depots[df_depots['Date'] == today_string]

    df_aggregated["Date"] = pd.to_datetime(
        df_aggregated["Date"], format="%Y-%m-%d")
    df_aggregated["Date"] = df_aggregated["Date"].dt.date

    app = create_page()

    app.run_server()
