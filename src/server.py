"""Module to centralize the applications related to Flask and Dash. This is a
necessary design to avoid circular imports accross Flask and Dash, still
being able to have Dash served by Flask.

For Dash, to avoid the error::

    dash.exceptions.NoLayoutException: The layout was `None` at the time that
    `run_server` was called. Make sure to set the `layout` attribute of your
    application before running the server.

The layout is defined as a dummy content, to be rendered later.

"""
from flask import Flask
from dash import Dash
from dash import html

server = Flask(__name__)
server.secret_key = "non-secret-key"
dash_app = Dash(__name__,  server=server, url_base_pathname='/report1/')

# ------------------------------------------------------------------------------
#   This definition of a dummy layout with just a string is necessary to avoid
#   the error:
#
#       dash.exceptions.NoLayoutException: The layout was `None` at the time
#       that `run_server` was called. Make sure to set the `layout` attribute
#       of your application before running the server.
# ------------------------------------------------------------------------------
dash_app.layout = html.Div("Empty")
