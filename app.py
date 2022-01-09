from flask import Flask
import glob
from pathlib import Path
from automation import run_analysis
from automation import comdirect_status_update

app = Flask(__name__)


@app.route("/")
def basic():
    return "It's Running"


@app.route("/test")
def test():
    return "It's Running a Test"


@app.route("/list")
def list_files():
    root_folder = Path.cwd().resolve()
    # list_files_folder = list(root_folder.glob("**/*"))
    list_files_folder = list(root_folder.glob("*"))
    list_files_names = [item.name for item in list_files_folder]
    list_files_names = "<br>".join(list_files_names)

    cfg_folder = Path.cwd().resolve() / "cfg"
    list_files_folder = list(cfg_folder.glob("*"))
    list_files_names_cfg = [item.name for item in list_files_folder]
    list_files_names_cfg = "<br>".join(list_files_names_cfg)

    list_files_names = list_files_names + "<br><br>" + list_files_names_cfg

    return list_files_names


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
