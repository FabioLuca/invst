from flask import Flask, request, render_template, redirect, url_for
from pathlib import Path
from automation import run_analysis
from automation import comdirect_status_update

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def basic():

    if request.method == 'GET':
        return render_template('app.html')

    if request.method == 'POST':
        analysis_symbol_name = request.form.get("analysis_symbol_name")
        print(analysis_symbol_name)
        return run_analysis.run_analysis(ticker_input=analysis_symbol_name.upper())


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


@app.route("/analysiscomplete", methods=['POST'])
def call_run_analysis_complete():
    run_analysis.run_analysis()
    return redirect(url_for('basic'))


@app.route("/analysis", methods=['POST'])
def call_run_analysis():
    analysis_symbol_name = request.form.get("analysis_symbol_name")
    print(analysis_symbol_name)
    # name = request.args['s']
    if analysis_symbol_name != "":
        run_analysis.run_analysis(ticker_input=analysis_symbol_name.upper())
    return redirect(url_for('basic'))


@app.route("/update", methods=['POST'])
def call_run_update():
    comdirect_status_update.run_update(wait_time=30)
    return redirect(url_for('basic'))


@app.route("/update1", methods=['POST'])
def call_run_update_part1():
    comdirect_status_update.run_update()
    return redirect(url_for('basic'))


@app.route("/update2", methods=['POST'])
def call_run_update_part2():
    comdirect_status_update.run_update()
    return redirect(url_for('basic'))


if __name__ == "__main__":
    app.run(debug=False,
            host="0.0.0.0",
            port=8080)
