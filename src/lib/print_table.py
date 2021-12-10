import pandas as pd
import json
from datetime import datetime
from pathlib import Path


def summary_table(results_summary, excel_filename):
    """Creates a presentation of the data from summary for evaluation. First
    creates a version to be displayed on the console to the user. Second
    creates Excel format (from Pandas) and then configure the same sheet to
    improve the formatting.

    """

    list_item = []

    print("{:<9} {:<10} {:<14} {:<12} {:<12} {:<12} {:<12} {:<9} {:<9} {:<9} {:<13} {:<14}".format(
        "Symbol",
        "Method",
        "Data Length",
        "Avg Vol",
        "Up Mov",
        "Down Mov",
        "Ratio Mov",
        "Last Day",
        "Prev Day",
        "Rel Gain",
        "Rel Gain Ref",
        "Rel Gain Comp"))
    for element in list(results_summary):
        print(
            "-----------------------------------------------------------------------------")
        symbol = list(element)[0]
        content = element[symbol]
        methods = list(content)

        for method in methods:

            parameters = content[method]

            for key in list(parameters.keys()):

                list_row = []

                list_row.append(symbol)
                list_row.append(method)
                list_row.append(key)
                list_row.append(parameters[key])

                tuple_row = tuple(list_row)

                list_item.append(tuple_row)

            print("{:<9} {:<10} {:<14} {:<12.3f} {:<12.3f} {:<12.3f} {:<12.3f} {:<9} {:<9} {:<9.2f} {:<13.2f} {:<14.2f}".format(
                symbol,
                method,
                content[method]["Analysis length"],
                content[method]["Average Volume"] / 1000000,
                content[method]["Up Movement"],
                content[method]["Down Movement"],
                content[method]["Ratio Movement"],
                content[method]["Last Day Event"],
                content[method]["Previous Day Event"],
                content[method]["Relative gain"] * 100,
                content[method]["Relative gain reference"] * 100,
                content[method]["Relative gain comparison"] * 100))

    # --------------------------------------------------------------------------
    #   Convert into a Pandas dataframe and pivor it, so columns are spread
    # --------------------------------------------------------------------------
    df = pd.DataFrame(list_item, columns=[
        'Symbol', 'Method', 'Parameter', 'Value'])

    df_pivot = df.pivot_table(index=['Symbol', 'Method'], columns=['Parameter'],
                              values=['Value'], aggfunc='sum')

    df_pivot = df_pivot.reset_index()

    new_columns = list(df_pivot.columns.get_level_values(
        0))[:2] + list(df_pivot.columns.get_level_values(1))[2:]

    df_pivot.columns = new_columns
    df_pivot = df_pivot.reset_index()
    df_pivot = df_pivot.reset_index()

    # --------------------------------------------------------------------------
    #   Save as Excel
    # --------------------------------------------------------------------------
    columns_order = ["Symbol",
                     "Method",
                     "Analysis length",
                     "Average Volume",
                     "Up Movement",
                     "Down Movement",
                     "Ratio Movement",
                     "Last Day Event",
                     "Previous Day Event",
                     "Relative gain",
                     "Relative gain reference",
                     "Relative gain comparison"]

    writer = pd.ExcelWriter(excel_filename, engine='xlsxwriter')
    df_pivot.to_excel(writer, sheet_name='Summary', columns=columns_order)

    workbook = writer.book
    worksheet = writer.sheets['Summary']

    format_text = workbook.add_format(
        {'num_format': 'General', 'align': 'left'})
    format_text_middle = workbook.add_format(
        {'num_format': 'General', 'align': 'center'})
    format_float = workbook.add_format({'num_format': '#,##0.000'})
    format_integer = workbook.add_format({'num_format': '#,##0'})
    format_percentage = workbook.add_format({'num_format': '0.00%'})
    format_headers = workbook.add_format(
        {'bold': True, 'text_wrap': True, 'valign': 'top', 'align': 'center',
         'bg_color': '#1F497D', 'font_color': '#FFFFFF'})

    format_buy = workbook.add_format({'bg_color':   '#4b9c09',
                                      'bold':       True,
                                      'font_color': '#000000'})
    format_hold = workbook.add_format({'bg_color':   '#DDDDDD',
                                       'font_color': '#AAAAAA'})
    format_sell = workbook.add_format({'bg_color':   '#871e17',
                                       'bold':       True,
                                       'font_color': '#FFFFFF'})
    format_dark_green = workbook.add_format({'bg_color':   '#65c75f',
                                             'font_color': '#000000'})
    format_green = workbook.add_format({'bg_color':   '#BDFB97',
                                        'font_color': '#000000'})
    format_yellow = workbook.add_format({'bg_color':   '#fadb75',
                                         'font_color': '#000000'})
    format_red = workbook.add_format({'bg_color':   '#FF797C',
                                      'font_color': '#000000'})
    format_dark_red = workbook.add_format({'bg_color':   '#e84848',
                                           'font_color': '#000000'})

    worksheet.set_column('B:B', 12, format_text)
    worksheet.set_column('C:C', 12, format_text)
    worksheet.set_column('D:D', 10, format_integer)
    worksheet.set_column('E:E', 16, format_integer)
    worksheet.set_column('F:H', 10, format_float)
    worksheet.set_column('I:J', 10, format_text_middle)
    worksheet.set_column('K:M', 12, format_percentage)

    range_cells = f"I2:J{df_pivot.shape[0] + 1}"

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': 'equal to',
                                               'value':    '"BUY"',
                                               'format':   format_buy})

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': 'equal to',
                                               'value':    '"HOLD"',
                                               'format':   format_hold})

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': 'equal to',
                                               'value':    '"SELL"',
                                               'format':   format_sell})

    ###### Ratio movement ######################################################

    range_cells = f"H2:H{df_pivot.shape[0] + 1}"

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '>',
                                               'value':    1.3,
                                               'format':   format_red})

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '>',
                                               'value':    1.1,
                                               'format':   format_yellow})

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '>',
                                               'value':    1,
                                               'format':   format_green})

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '>',
                                               'value':    0,
                                               'format':   format_dark_green})

    ###### Relative gain comparison ############################################

    range_cells = f"M2:M{df_pivot.shape[0] + 1}"

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '>',
                                               'value':    0.05,
                                               'format':   format_dark_green})

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '>',
                                               'value':    0,
                                               'format':   format_green})

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '>',
                                               'value': -0.02,
                                               'format':   format_yellow})

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '>',
                                               'value': -0.10,
                                               'format':   format_red})

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '<=',
                                               'value': -0.10,
                                               'format':   format_dark_red})

    ###### Relative gain & Relative gain reference #############################

    range_cells = f"K2:L{df_pivot.shape[0] + 1}"

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '>',
                                               'value':    0.2,
                                               'format':   format_dark_green})

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '>',
                                               'value':    0.05,
                                               'format':   format_green})

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '>',
                                               'value':    0.00,
                                               'format':   format_yellow})

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '>',
                                               'value': -0.05,
                                               'format':   format_red})

    worksheet.conditional_format(range_cells, {'type':     'cell',
                                               'criteria': '<=',
                                               'value': -0.05,
                                               'format':   format_dark_red})

    worksheet.set_row(0, None, format_headers)

    # --------------------------------------------------------------------------
    #   Configure the headers and adds the freezed pane on the header and
    #   auto-filter.
    # --------------------------------------------------------------------------
    col_num = 1
    for value in columns_order:
        worksheet.write(0, col_num, value, format_headers)
        col_num = col_num + 1

    worksheet.freeze_panes(1, 0)
    worksheet.autofilter(f"A1:M{df_pivot.shape[0] + 1}")

    # --------------------------------------------------------------------------
    #   Adds hyperlinks to the table.
    # --------------------------------------------------------------------------
    today_string = datetime.today().strftime('%Y-%m-%d')
    method_config_folder = Path.cwd().resolve() / "src" / \
        "lib_analysis" / "methods" / "display_config"
    files = list(filter(Path.is_file, method_config_folder.glob('**/*.json')))

    method_savenames = {}
    for method_file in files:
        with open(method_file) as json_file:
            data = json.load(json_file)
        method_name = data["general"]["reference_name"]
        method_savename = data["general"]["save_name"]
        method_savenames[method_name] = method_savename

    for row_num in range(df_pivot.shape[0]):
        symbol_value = df_pivot["Symbol"].iloc[row_num]
        method_value = df_pivot["Method"].iloc[row_num]
        method_file = method_savenames[method_value]
        string_fomular = f'=HYPERLINK(_xlfn.CONCAT(LEFT(CELL("filename"),SEARCH("[",CELL("filename"))-1),"analysis\{today_string}\Analysis {method_file} {symbol_value}.html"), "{symbol_value}")'
        worksheet.write_formula(f"B{row_num + 2}", string_fomular)

    writer.save()

    return df_pivot
