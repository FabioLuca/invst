from flask import Flask
import glob
from pathlib import Path
from automation import run_analysis
from automation import comdirect_status_update
from src.lib.config import Config

app = Flask(__name__)


@app.route("/")
def basic():
    return "It's Running"


@app.route("/test")
def test():
    return "It's Running a Test"


@app.route("/list")
def list_files():

    output_string = ""
    root_folder = Path.cwd().resolve()
    output_string = str(root_folder) + "<br>"
    output_string = output_string + "<br>--------------------<br><br>"

    # list_files_folder = list(root_folder.glob("**/*"))
    list_files_folder = root_folder.glob("*")
    for item in list_files_folder:
        if item.is_dir():
            output_string = output_string + f"<b>{item.name}</b><br>"
            sublist_files_folder = item.glob("*")
            for subitem in sublist_files_folder:
                if subitem.is_dir():
                    output_string = output_string + \
                        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>{subitem.name}</b><br>"
                else:
                    output_string = output_string + \
                        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{subitem.name}<br>"
        else:
            output_string = output_string + f"{item.name}<br>"

    output_string = output_string + "<br>--------------------<br><br>"

    with open(root_folder / "cfg" / "api-cfg.json") as f:
        contents = f.read()

    output_string = output_string + contents

    output_string = output_string + "<br>--------------------<br><br>"

    with open(root_folder / "cfg" / "user" / "api-cfg-access.json") as f:
        contents = f.read()

    output_string = output_string + contents

    # list_files_folder = list(root_folder.glob("**/*"))
    # # cfg_folder = Path.cwd().resolve() / "cfg"
    # # list_files_folder = list(cfg_folder.glob("*"))
    # list_files_names = [item.name for item in list_files_folder]
    # list_files_names = "<br>".join(list_files_names)

    # output_string = output_string + list_files_names
    # output_string = output_string + "--------------------<br><br>"

    return output_string


@ app.route("/analysis")
def call_run_analysis():
    run_analysis.run_analysis()
    return "Running market analysis"


@ app.route("/update")
def call_run_update():
    comdirect_status_update.run_update()
    return "Running update from Comdirect"


if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=8080)
