from flask import Flask
from automation import run_analysis
from automation import comdirect_status_update

app = Flask(__name__)


@app.route("/")
def basic():
    return "It's Running"


@app.route("/analysis")
def call_run_analysis():
    return run_analysis.run_analysis()


@app.route("/update")
def call_run_update():
    return comdirect_status_update.run_update()


if __name__ == "__main__":
    app.run(debug=False,
            host="0.0.0.0",
            port=8080)
