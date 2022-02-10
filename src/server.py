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
from pathlib import Path
from src.lib.config import Config
from src.storage import Storage


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

# ------------------------------------------------------------------------------
#   Starts logger, config and storage
# ------------------------------------------------------------------------------

LOGGER_NAME = "invst.app"

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
config.load_config(filename=config_parameters_file)

storage = Storage(config=config, logger_name=LOGGER_NAME)
