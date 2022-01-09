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

    return output_string


@ app.route("/analysis")
def call_run_analysis():
    run_analysis.run_analysis()
    return "Running market analysis"


@ app.route("/update")
def call_run_update():
    comdirect_status_update.run_update(wait_time=20)
    return "Running update from Comdirect"


@ app.route("/update1")
def call_run_update_part1():
    comdirect_status_update.run_update()
    return "Running update from Comdirect: Part 1"


@ app.route("/update2")
def call_run_update_part2():
    comdirect_status_update.run_update()
    return "Running update from Comdirect: Part 2"


if __name__ == "__main__":
    app.run(debug=False,
            host="0.0.0.0",
            port=8080)
