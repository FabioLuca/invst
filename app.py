from flask import Flask, request, render_template, redirect, url_for
from dash import Dash
# from werkzeug.middleware.dispatcher import DispatcherMiddleware
# from werkzeug.serving import run_simple
# import dash_html_components as html
from pathlib import Path
from automation import run_analysis
from automation import comdirect_status_update
from automation import comdirect_status_report

server = Flask(__name__)
dash_app = Dash(__name__, server=server, url_base_pathname='/report1/')
# html.Div([html.H1('Hi there, I am app1 for dashboards')])
#dash_app.layout = comdirect_status_report.app.layout
comdirect_status_report.make_report(dash_app)


@server.route("/", methods=['POST', 'GET'])
def basic():

    if request.method == 'GET':
        return render_template('app.html')

    if request.method == 'POST':
        analysis_symbol_name = request.form.get("analysis_symbol_name")
        print(analysis_symbol_name)
        return run_analysis.run_analysis(ticker_input=analysis_symbol_name.upper())


@server.route("/test")
def test():
    return "It's Running a Test"


@server.route("/list")
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


@server.route("/analysiscomplete", methods=['POST'])
def call_run_analysis_complete():
    run_analysis.run_analysis()
    return redirect(url_for('basic'))


@server.route("/analysis", methods=['POST'])
def call_run_analysis():
    analysis_symbol_name = request.form.get("analysis_symbol_name")
    print(analysis_symbol_name)
    # name = request.args['s']
    if analysis_symbol_name != "":
        run_analysis.run_analysis(ticker_input=analysis_symbol_name.upper())
    return redirect(url_for('basic'))


@server.route("/update", methods=['POST'])
def call_run_update():
    comdirect_status_update.run_update(mode=3, wait_time=30)
    return redirect(url_for('basic'))


@server.route("/update1", methods=['POST', 'GET'])
def call_run_update_part1():
    comdirect_status_update.run_update(mode=1)
    return redirect(url_for('basic'))


@server.route("/update2", methods=['POST', 'GET'])
def call_run_update_part2():
    comdirect_status_update.run_update(mode=2)
    return redirect(url_for('basic'))


@server.route('/report', methods=['POST', 'GET'])
def render_report():
    return redirect('/report1/')


# app = DispatcherMiddleware(server, {
#     '/dash1': comdirect_status_report.app  # dash_app1.server
# })


if __name__ == "__main__":
    server.run(debug=False,
               host="0.0.0.0",
               port=8080)
