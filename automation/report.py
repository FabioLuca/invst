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
from dash_table.Format import Format, Group, Prefix, Scheme, Symbol, Align, Sign
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------------------
#   Get all the files which contain data to be displayed. The files must be
#   all in the "export" folder, and named with the pattern
#   "Export_Comdirect_" to be included in the analysis.
# ------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------
#   Make a Dash application for displaying the charts. Dash will
#   automatically load the .css which are in the assets folder, so there is
#   no need to pass them. For that, this method of caalling the app is
#   necessary: app = dash.Dash(__name__)
# ------------------------------------------------------------------------------
app = dash.Dash(__name__)

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

layout_charts = go.Layout(
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

fig_aggregated_current_value.update_layout(layout_charts)

fig_depots_current_value = px.area(
    df_depots,
    x="Date",
    y="Current Value",
    color="WKN")

fig_depots_current_value.update_layout(layout_charts)

app.layout = html.Div(
    children=[
        html.H1(children='Results'),
        ################ CHART 1 ###############################################
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
        ################ CHART 2 ###############################################
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
        ################ TABLE 1 ###############################################
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
                    style_cell=dict(
                        minWidth='50px',
                        width='50px',
                        maxWidth='100px',
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
                    ],
                    style_data_conditional=[
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
                )
            ]
        ),
        ################ TABLE 2 ###############################################
        html.Div(
            [
                html.H3(children='Depots values'),
                # html.Div(
                #    children='Dash: A web application framework for Python.'),
                # dash_table.DataTable(id='tweet_table')
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
        ################ END ###################################################
    ]
)


if __name__ == "__main__":

    app.run_server()