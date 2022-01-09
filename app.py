from flask import Flask
import glob
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
    list_files_folder = glob.glob("/*")
    list_string = ", ".join(list_files_folder)
    return list_string


@ app.route("/analysis")
def call_run_analysis():
    run_analysis.run_analysis()
    return "Running market analysis"


@ app.route("/update")
def call_run_update():
    comdirect_status_update.run_update()
    return "Running update from Comdirect"


if __name__ == "__main__":
    app.run(debug=False,
            host="0.0.0.0",
            port=8080)
