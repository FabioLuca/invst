from flask import Flask, request, render_template
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


html_analysis = """
    <form action="analysis" method="post">
    <p>Symbol <input type = "text" name = "symbolname" /></p>
    <p><input type = "submit" value = "Submit" /></p>
    """


@app.route("/analysis_completa")
def call_run_analysis_completa():
    return run_analysis.run_analysis()


@app.route("/analysis", methods=['POST', 'GET'])
def call_run_analysis():

    if request.method == 'GET':
        return html_analysis

    if request.method == 'POST':
        name = request.form.get("symbolname")
        print(name)
        # name = request.args['s']
        return run_analysis.run_analysis(ticker_input=name.upper())


@app.route("/update")
def call_run_update():
    return comdirect_status_update.run_update(wait_time=30)


@app.route("/update1")
def call_run_update_part1():
    comdirect_status_update.run_update()
    return "Running update from Comdirect: Part 1"


@app.route("/update2")
def call_run_update_part2():
    comdirect_status_update.run_update()
    return "Running update from Comdirect: Part 2"


if __name__ == "__main__":
    app.run(debug=False,
            host="0.0.0.0",
            port=8080)
