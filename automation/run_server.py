import os
from flask import Flask
from automation import run_analysis

app = Flask(__name__)


@app.route("/")
def call_run_analysis():
    return run_analysis.run_analysis()


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0",
            port=int(os.environ.get("PORT", 8080)))
