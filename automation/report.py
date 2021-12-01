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

    layout = go.Layout(
        autosize=True,
        height=700,
        margin=dict(
            l=50, r=50, b=100, t=100, pad=4
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
            )
        ]

    )

    app.run_server()
