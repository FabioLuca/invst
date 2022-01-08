import os
from flask import Flask
from automation import run_analysis

app = Flask(__name__)


@app.get("/")
def basic():
    return "Running"


@app.get("/run")
def call_run_analysis():
    return run_analysis.run_analysis()


if __name__ == "__main__":
    app.run(debug=True,
            host="localhost",
            port=8080)

    # port=int(os.environ.get("PORT", 8080)))
