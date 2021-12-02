"""Automation script to display charts and reports of the data collected and
stored in the Excel files in the `export` folder. The script will parse the
data in the files.

This script is based on Dash and Plotly, and the execution will result into a
server which can be accessed by the addressed informed on the console, for
example: http://127.0.0.1:8050/

Only the files matching the pattern `Export_Comdirect_` are evaluated.

"""

from pathlib import Path
from dash import html
from dash import dcc
from dash import dash_table
from dash.dash_table.Format import Sign
from dash_table import FormatTemplate
from dash_table.Format import Format, Group, Prefix, Scheme, Symbol, Align
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


if __name__ == "__main__":

    # --------------------------------------------------------------------------
    #   Get all the files which contain data to be displayed. The files must be
    #   all in the "export" folder, and named with the pattern
    #   "Export_Comdirect_" to be included in the analysis.
    # --------------------------------------------------------------------------
    folder = Path.cwd().resolve() / "export"
    files = list(filter(Path.is_file, folder.glob('**/Export_Comdirect_*')))

    i = 0
    for file in files:

        df_file_aggregated = pd.read_excel(
            file, sheet_name="Depot Positions Aggregated")
        df_file_depots = pd.read_excel(
            file, sheet_name="Depot Positions")

        if i == 0:
            df_aggregated = df_file_aggregated
            df_depots = df_file_depots
        else:
            df_aggregated = df_aggregated.append(df_file_aggregated)
            df_depots = df_depots.append(df_file_depots)

        i = i + 1

    # --------------------------------------------------------------------------
    #   Make a Dash application for displaying the charts
    # --------------------------------------------------------------------------
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__,
                    external_stylesheets=external_stylesheets)

    # money = dash_table.FormatTemplate.money(2)
    percentage = dash_table.FormatTemplate.percentage(2)

    money = Format(
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

    percentage = Format(
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

    columns = [
        dict(id="Date", name="Date"),
        dict(id="WKN", name="WKN"),
        dict(id="Quantity", name="Quantity",
             type='numeric'),
        dict(id="Available Quantity", name="Available Quantity",
             type='numeric'),
        dict(id="Hedgeability", name="Hedgeability"),
        dict(id="Purchase Price", name="Purchase Price",
             type='numeric',
             format=money),
        dict(id="Current Price", name="Current Price",
             type='numeric',
             format=money),
        dict(id="Purchase Value", name="Purchase Value",
             type='numeric',
             format=money),
        dict(id="Current Value", name="Current Value",
             type='numeric',
             format=money),
        dict(id="Profit/Loss Purchase Absolute Value",
             name="Profit/Loss from Purchase Absolute Value",
             type='numeric',
             format=money),
        dict(id="Profit/Loss Purchase Relative",
             name="Profit/Loss from Purchase Relative",
             type='numeric',
             format=percentage),
        dict(id="Profit/Loss Previous Day Absolute Value",
             name="Profit/Loss from Previous Day Absolute Value",
             type='numeric',
             format=money),
        dict(id="Profit/Loss Previous Day Relative",
             name="Profit/Loss from Previous Day Relative",
             type='numeric',
             format=percentage)
    ]

    layout = go.Layout(
        autosize=True,
        height=600,
        margin=dict(
            l=100, r=200, b=60, t=40, pad=4
        ),
        paper_bgcolor="LightSteelBlue"
    )

    fig_aggregated_current_value = px.line(
        df_aggregated,
        x="Date",
        y="Depot Aggregated Current Value")
    # title="Aggregated Depot current value")

    fig_aggregated_current_value.update_layout(layout)

    fig_depots_current_value = px.area(
        df_depots,
        x="Date",
        y="Current Value",
        color="WKN")

    fig_depots_current_value.update_layout(layout)

    app.layout = html.Div(
        children=[
            html.H1(children='Results'),
            html.Div(
                [
                    html.H3(children='Aggregated depot current value'),
                    # html.Div(
                    #    children='Dash: A web application framework for Python.'),
                    dcc.Graph(
                        id='fig_aggregated_current_value',
                        figure=fig_aggregated_current_value
                    )
                ]
            ),
            html.Div(
                [
                    html.H3(children='Depots current values'),
                    # html.Div(
                    #    children='Dash: A web application framework for Python.'),
                    dcc.Graph(
                        id='fig_depots_current_value',
                        figure=fig_depots_current_value
                    )
                ]
            ),
            html.Div(
                [
                    html.H3(children='Depots values'),
                    # html.Div(
                    #    children='Dash: A web application framework for Python.'),
                    # dash_table.DataTable(id='tweet_table')
                    dash_table.DataTable(
                        id='table',
                        filter_action='native',
                        sort_action='native',
                        # fixed_rows={'headers': True, 'data': 0},
                        page_size=20,
                        sort_mode='multi',
                        sort_by=[{'column_id': 'Date', 'direction': 'desc'},
                                 {'column_id': 'Profit/Loss Previous Day Absolute Value',
                                     'direction': 'desc'},
                                 {'column_id': 'WKN', 'direction': 'asc'}],
                        columns=columns,
                        data=df_depots.to_dict('records'),
                        style_cell=dict(
                            minWidth='10px',
                            width='10px',
                            maxWidth='10px',
                            # textAlign='left',
                            whiteSpace='normal'),
                        style_header=dict(
                            backgroundColor='rgb(150, 150, 150)',
                            color='black',
                            textAlign='center',
                            fontWeight='bold',
                            whiteSpace="normal",
                            height="auto"),
                        style_data=dict(
                            backgroundColor="lavender"),
                        style_table={'overflowX': 'auto'},
                        style_cell_conditional=[
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
                            # {
                            #     'if':
                            #     {
                            #         'column_id': 'Profit/Loss Previous Day Absolute Unit',
                            #     },
                            #     'display': 'None'
                            # },
                            # {
                            #     'if':
                            #     {
                            #         'column_id': 'WKN'
                            #     },
                            #     'width': '130px'
                            # },
                        ],
                        style_data_conditional=[
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
                            },
                        ]
                    )
                ]
            )
        ]
    )

    app.run_server()
