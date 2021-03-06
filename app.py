from flask import Flask, request, render_template, redirect, url_for, flash
from pathlib import Path
from automation import run_analysis
from automation import comdirect_status_update
from automation import comdirect_status_report
from src import server


@server.server.route("/", methods=['POST', 'GET'])
def basic():

    if request.method == 'GET':
        return render_template('app.html')

    if request.method == 'POST':
        analysis_symbol_name = request.form.get("analysis_symbol_name")
        return run_analysis.run_analysis(ticker_input=analysis_symbol_name.upper())


@server.server.route("/test")
def test():
    return "It's Running a Test"


@server.server.route("/list")
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


@server.server.route("/analysis/<symbol>", methods=['GET', 'POST'])
def call_run_analysis_list(symbol: str):
    """Method for processing an analysis for a defined symbol, passing the
    symbols as part of the URL. This is intended to be used for automation
    tasks, such as by schedulers. For passing a list of symbols the values need
    to be separated by semicolon (";"). Additionally, passing the keyword
    ``complete`` will trigger the function using the internally defined list of
    symbols.

    Example
    -------

    As example of usage for a single value, where the Amazon stock is
    evaluated::

        <base_url>/analysis/AMZN

    As example of usage for a list of values, where the Amazon, Google and 3D
    stocks are evaluated::

        <base_url>/analysis/AMZN;GOOG;MMM

    As example of usage for the internal list::

        <base_url>/analysis/complete

    """
    if request.method == 'GET':

        symbol = symbol.upper()

        if symbol == "COMPLETE":
            run_analysis.run_analysis()
        else:
            if ";" in symbol:
                symbol_list = symbol.split(";")
            else:
                symbol_list = [symbol]
            run_analysis.run_analysis(ticker_input=symbol_list)

        return redirect(url_for('basic'))


@server.server.route("/analysis", methods=['POST'])
def call_run_analysis():
    analysis_symbol_name = request.form.get("analysis_symbol_name")
    analysis_symbol_name = analysis_symbol_name.upper()
    if analysis_symbol_name != "":
        analysis_symbol_name = analysis_symbol_name.replace(" ", "")
        analysis_symbol_name = analysis_symbol_name.replace(",", ";")
        if ";" in analysis_symbol_name:
            symbol_list = analysis_symbol_name.split(";")
        else:
            symbol_list = [analysis_symbol_name]
        run_analysis.run_analysis(ticker_input=symbol_list)

    return redirect(url_for('basic'))


@server.server.route("/update", methods=['POST'])
def call_run_update():
    comdirect_status_update.run_update(mode=3, wait_time=30)
    return redirect(url_for('basic'))


@server.server.route("/update1", methods=['POST', 'GET'])
def call_run_update_part1():
    comdirect_status_update.run_update(mode=1)
    flash("Waiting for the TAN authentication...", "comdirect-status")
    return redirect(url_for('basic'))


@server.server.route("/update2", methods=['POST', 'GET'])
def call_run_update_part2():
    comdirect_status_update.run_update(mode=2)
    return redirect(url_for('basic'))


@server.server.route('/report', methods=['POST', 'GET'])
def render_report():
    comdirect_status_report.make_report(server.dash_app)
    return redirect('/report1/')


@server.server.route('/startdb', methods=['POST', 'GET'])
def start_database():
    server.storage.start_stop_instance(start_stop="START")
    return redirect(url_for('basic'))


@server.server.route('/close', methods=['POST', 'GET'])
def close_database():
    server.storage.close()
    return redirect(url_for('basic'))


if __name__ == "__main__":
    server.server.run(debug=False,
                      host="0.0.0.0",
                      port=8080)
