"""This modules is used to generate reports of the stock analysis."""
import inspect
import pathlib
import json
from datetime import datetime
from pathlib import Path
from plotly.subplots import make_subplots
from src.lib.config import Config

LOGGER_NAME = "invst.report_analysis"


class ReportAnalysis:

    def __init__(self, name) -> None:
        self.name = name
        self.savename = name
        self.config_general = None
        self.config_components = None

    def load_config(self):
        """Load the configuration for the type of analysis. For each analysis,
        there is a specific display, so first the function need to identify the
        requester by analyzing the stack.
        """
        frm = inspect.stack()[2]
        module = inspect.getmodule(frm[0])
        module_split = module.__name__.split(".")
        method = module_split[-1]

        config_file = Path.cwd().resolve() / "src" / "lib" / "analysis" / "methods" / "display_config" / \
            f"{method}.json"

        with open(config_file) as json_file:
            config_dict = json.load(json_file)

        self.config_general = config_dict["general"]
        self.config_components = config_dict["components"]

        self.name = self.config_general["display_name"]
        self.savename = self.config_general["save_name"]

        config_local_file = Path.cwd().resolve() / "cfg" / "local.json"
        config = Config(logger_name=LOGGER_NAME)
        config.load_config(filename=config_local_file)
        self.store_folder = Path(config.local_config["paths"]["data_storage"])

    def present_analysis(self):
        """Creates a HTML report with the timeseries data (candlestick), with the
        results from time analysis, pattern analysis and the indications for buy,
        sell or hold.
        """
        self.load_config()
        self.create_plot()

    def create_location(self, path: pathlib):

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

    def create_plot(self):
        """Generates the report for an analysis.
        """
        today_string = datetime.today().strftime('%Y-%m-%d')

        # ----------------------------------------------------------------------
        #   Define de plot object with subplots, getting all the information
        #   from the central dictionary.
        # ----------------------------------------------------------------------
        specs_subplots = []
        for element in self.config_general["subplots_secondary_y_axis"]:
            dict_element = {"secondary_y": element}
            specs_subplots.append([dict_element])

        fig_subplot = make_subplots(
            rows=self.config_general["count_subplots_rows"],
            cols=self.config_general["count_subplots_columns"],
            shared_xaxes=self.config_general["shared_x_axes"],
            vertical_spacing=self.config_general["vertical_spacing"],
            # subplot_titles=("subtitle 1", "subtitle 2"),
            row_heights=self.config_general["subplots_rows_heights"],
            specs=specs_subplots,
        )

        # ----------------------------------------------------------------------
        #   Define the axis information
        # ----------------------------------------------------------------------
        y = 1
        x = 1

        for secondary_y, title_y_left, title_y_right, title_x, categorical_y, category_y_order in zip(
            self.config_general["subplots_secondary_y_axis"],
            self.config_general["subplots_left_y_axis_titles"],
            self.config_general["subplots_right_y_axis_titles"],
            self.config_general["subplots_x_axis_titles"],
            self.config_general["categorical_y"],
            self.config_general["categorical_y_order"]

        ):
            fig_subplot["layout"]["yaxis" + str(y)]["title"] = title_y_left
            if categorical_y:
                fig_subplot["layout"]["yaxis" + str(y)]["type"] = "category"
                fig_subplot["layout"]["yaxis" +
                                      str(y)]["categoryorder"] = "array"

                fig_subplot["layout"]["yaxis" +
                                      str(y)]["categoryarray"] = category_y_order

            y = y + 1
            if secondary_y:
                fig_subplot["layout"]["yaxis" +
                                      str(y)]["title"] = title_y_right
                y = y + 1
            if not title_x == "":
                fig_subplot["layout"]["xaxis" + str(x)]["title"] = title_x
                x = x + 1

        # ----------------------------------------------------------------------
        #   Define the plot entity for OHCP
        # ----------------------------------------------------------------------
        trace_base = {
            "x": self.ohlc_dataset.index,
            "open": self.ohlc_dataset["Open"],
            "high": self.ohlc_dataset["High"],
            "low": self.ohlc_dataset["Low"],
            "close": self.ohlc_dataset["Close"],
            "type": "candlestick",
            "name": self.symbol,
            "showlegend": False,
            # "text": self.ohlc_dataset["Name Pattern"],
        }

        # ----------------------------------------------------------------------
        #   Add the color information for the candlestick chart
        # ----------------------------------------------------------------------
        plot_ohcp_config = {"increasing_line_color": self.config_general["ohlc_increasing_color"],
                            "decreasing_line_color": self.config_general["ohlc_decreasing_color"]}
        trace_base = {**trace_base, **plot_ohcp_config}
        fig_subplot.append_trace(trace_base, row=1, col=1)
        # fig_subplot["layout"].update(shapes=shapes)

        # ----------------------------------------------------------------------
        #   Adjust the font size for the subplot axis
        # ----------------------------------------------------------------------
        for i in fig_subplot["layout"]["annotations"]:
            i["font"] = dict(size=10, color="#ff0000")
            i["font"]["size"] = 5

        # ----------------------------------------------------------------------
        #   Each individual plot is added to the overall charts based on the
        #   information from the respective .json file, where for each signal
        #   the configuration is stored.
        #   Before adding, it is verified if the signal is present on the Pandas
        #   dataframe.
        # ----------------------------------------------------------------------
        for component in self.config_components:

            config = self.config_components[component]

            if component not in self.ohlc_dataset.columns:
                continue

            # ------------------------------------------------------------------
            #   LINES
            # ------------------------------------------------------------------
            if (config["type"] == "Line" and config["show"]):
                yaxis = None
                trace_add = {
                    "x": self.ohlc_dataset.index,
                    "y": self.ohlc_dataset[component],
                    "type": "scatter",
                    "mode": "lines",
                    "opacity": config["opacity"],
                    "line": {
                        "width": config["width"],
                        "color": config["color"],
                        "dash": config["dash"],
                        "shape": config["shape"],
                    },
                    "name": config["display_name"],
                }
                fig_subplot.add_trace(
                    trace_add,
                    row=config["subplot_vertical"],
                    col=config["subplot_horizontal"],
                    secondary_y=config["secondary_y"],
                )

            # ------------------------------------------------------------------
            #   BARS
            # ------------------------------------------------------------------
            elif (config["type"] == "Bar" and config["show"]):
                color_pos = config["color_positive"]
                color_neg = config["color_negative"]
                color_sequence = self.ohlc_dataset[component].values.tolist()
                for (i, item) in enumerate(color_sequence):
                    if item < 0:
                        color_sequence[i] = color_neg
                    else:
                        color_sequence[i] = color_pos
                trace_add = {
                    "x": self.ohlc_dataset.index,
                    "y": self.ohlc_dataset[component],
                    "type": "bar",
                    "opacity": config["opacity"],
                    "name": config["display_name"],
                    "marker": dict(color=color_sequence),
                }
                fig_subplot.add_trace(
                    trace_add,
                    row=config["subplot_vertical"],
                    col=config["subplot_horizontal"],
                    secondary_y=config["secondary_y"],
                )
            # # --------------------------------------------------------------
            # #   MARKS
            # # --------------------------------------------------------------
            # elif (
            #     plot_config["type"] == "Mark"
            #     and plot_config["show"]
            #     and basic_config["enable"]
            # ):

            #     for index, row in series.iterrows():
            #         if row[basic_config["name"]] > 0:
            #             new_annot = {
            #                 "x": index,
            #                 "y": series["High"][index],
            #                 "xref": "x",
            #                 "yref": "y",
            #                 "text": name[8:] + ": Bear",
            #                 "showarrow": False,
            #                 "arrowhead": 7,
            #                 "ax": 0,
            #                 "ay": -20,
            #                 "textangle": -90,
            #                 "align": "left",
            #                 "valign": "top",
            #                 "xanchor": "center",
            #                 "yanchor": "bottom",
            #                 "font": {
            #                     "size": plot_config["size"],
            #                     "color": plot_config["color"],
            #                 },
            #                 # "font": {"size": 8, "color": "#aaaaaa"},
            #             }
            #             # annotations.append(new_annot)
            #             fig_subplot.add_annotation(
            #                 new_annot,
            #                 row=plot_config["subplot_vertical"],
            #                 col=1,
            #                 secondary_y=plot_config["secondary_y"],
            #             )
            #         elif row[basic_config["name"]] < 0:
            #             new_annot = {
            #                 "x": index,
            #                 "y": series["Low"][index],
            #                 "xref": "x",
            #                 "yref": "y",
            #                 "text": name[8:] + ": Bull",
            #                 "showarrow": False,
            #                 "arrowhead": 7,
            #                 "ax": 0,
            #                 "ay": 20,
            #                 "textangle": -90,
            #                 "align": "right",
            #                 "valign": "bottom",
            #                 "xanchor": "center",
            #                 "yanchor": "top",
            #                 "font": {
            #                     "size": plot_config["size"],
            #                     "color": plot_config["color"],
            #                 },
            #             }
            #             # annotations.append(new_annot)
            #             fig_subplot.add_annotation(
            #                 new_annot, row=plot_config["subplot_vertical"], col=1,
            #             )
            # # --------------------------------------------------------------
            # #   MARKS BUY SELL
            # # --------------------------------------------------------------
            # elif plot_config["type"] == "Mark Buy/Sell":
            #     for index, row in series.iterrows():
            #         # ------------------------------------------------------
            #         #   Add the markers for the strategy decision
            #         # ------------------------------------------------------
            #         if row[name] == Const.BUY:
            #             new_annot = {
            #                 "x": index,
            #                 "y": series["High"][index],
            #                 "xref": "x",
            #                 "yref": "y",
            #                 "text": "<b>BUY</b><br>"
            #                 + plot_config[name][
            #                     "Shortname"
            #                 ],  # "".join(i[0] for i in name[9:].split()).upper(),
            #                 "showarrow": True,
            #                 "arrowhead": 3,
            #                 "arrowcolor": plot_config[name]["Buy"]["Color"],
            #                 "arrowsize": 2,
            #                 "ax": 0,
            #                 "ay": -60,
            #                 "textangle": 0,
            #                 "align": "center",
            #                 "valign": "top",
            #                 "xanchor": "center",
            #                 "yanchor": "bottom",
            #                 "font": {
            #                     "size": plot_config[name]["Buy"]["Size"],
            #                     "color": plot_config[name]["Buy"]["Color"],
            #                 },
            #             }
            #             # annotations.append(new_annot)
            #             fig_subplot.add_annotation(
            #                 new_annot, row=1, col=1)
            #         elif row[name] == Const.SELL:
            #             new_annot = {
            #                 "x": index,
            #                 "y": series["Low"][index],
            #                 "xref": "x",
            #                 "yref": "y",
            #                 "text": "<b>SELL</b><br>"
            #                 + plot_config[name][
            #                     "Shortname"
            #                 ],  # + "".join(i[0] for i in name[9:].split()).upper(),
            #                 "showarrow": True,
            #                 "arrowhead": 3,
            #                 "arrowcolor": plot_config[name]["Sell"]["Color"],
            #                 "arrowsize": 2,
            #                 "ax": 0,
            #                 "ay": 60,
            #                 "textangle": 0,
            #                 "align": "center",
            #                 "valign": "bottom",
            #                 "xanchor": "center",
            #                 "yanchor": "top",
            #                 "font": {
            #                     "size": plot_config[name]["Sell"]["Size"],
            #                     "color": plot_config[name]["Sell"]["Color"],
            #                 },
            #             }
            #             # annotations.append(new_annot)
            #             fig_subplot.add_annotation(
            #                 new_annot, row=1, col=1)

        # dict_annotation = {"annotations": annotations}

        """-------------------------------------------------------------------------
            Add the general config
        -------------------------------------------------------------------------"""
        # layout_base = {**layout_base, **PlotConfig.PLOT_CONFIG}
        # layout_base = {**layout_base, **dict_annotation}

        """-------------------------------------------------------------------------
            Pass the final config dict
        -------------------------------------------------------------------------"""
        # layout = go.Layout(layout_base)
        # fig_subplot.update_layout(layout=layout)

        # ----------------------------------------------------------------------
        #   Update the layout.
        # ----------------------------------------------------------------------
        layout_base = {
            "title": {
                "text": f"{self.name} {self.symbol.upper()}: {today_string}",
                "font": {
                    "size": self.config_general["title_font_size"]
                },
            },
            "legend_title": {
                "text": "Legend:",
                "font": {
                    "size": self.config_general["legend_title_font_size"]
                }
            },
        }
        fig_subplot.update_layout(layout_base)

        # darker_tint = 'rgba(40, 40, 40, 255)'
        # dark_tint = 'rgba(50, 50, 50, 255)'
        # middle_tint = 'rgba(70, 70, 70, 255)'
        # light_tint = 'rgba(90, 90, 90, 255)'
        # lighter_tint = 'rgba(150, 150, 150, 255)'
        # lightest_tint = 'rgba(200, 200, 200, 255)'

        # layout_charts = go.Layout(
        #     autosize=True,
        #     height=600,
        #     margin=dict(l=100, r=200, b=60, t=40, pad=4),
        #     plot_bgcolor=middle_tint,
        #     paper_bgcolor=dark_tint,
        #     xaxis={'automargin': True,
        #            'gridcolor': light_tint,
        #            'gridwidth': 2,
        #            'linecolor': lighter_tint,
        #            'ticks': '',
        #            'title': {'standoff': 15},
        #            'zerolinecolor': lighter_tint,
        #            'zerolinewidth': 2,
        #            'tickfont': {
        #                'color': lightest_tint
        #            },
        #            'title': {
        #                'font': {
        #                    'color': lightest_tint
        #                }
        #            }
        #            },
        #     yaxis={'automargin': True,
        #            'gridcolor': light_tint,
        #            'gridwidth': 2,
        #            'linecolor': lighter_tint,
        #            'ticks': '',
        #            'title': {'standoff': 15},
        #            'zerolinecolor': lighter_tint,
        #            'zerolinewidth': 2,
        #            'tickfont': {
        #                'color': lightest_tint
        #            },
        #            'title': {
        #                'font': {
        #                    'color': lightest_tint
        #                }
        #            }
        #            },
        #     legend={
        #         'bgcolor': middle_tint,
        #         'bordercolor': darker_tint,
        #         'borderwidth': 2,
        #         'font': {
        #             'color': lightest_tint
        #         }
        #     },
        # )
        # fig_subplot.update_layout(layout_charts)

        fig_subplot.update_layout(
            xaxis_rangeslider_visible=self.config_general["xaxis_rangeslider_visible"],
            bargap=self.config_general["bargap"],
        )

        # ----------------------------------------------------------------------
        #   Changes the theme of the plot
        # ----------------------------------------------------------------------
        fig_subplot.layout.template = self.config_general["theme"]

        # ----------------------------------------------------------------------
        #   Set up the path to save the file and save the document if necessary.
        # ----------------------------------------------------------------------
        if self.save_analysis:
            save_file_path = self.store_folder / "analysis" / today_string / \
                f"Analysis {self.savename} {self.symbol}.html"
            self.create_location(save_file_path.parent.resolve())
            fig_subplot.write_html(save_file_path)

        # ----------------------------------------------------------------------
        #   Save and show the HTML report
        # ----------------------------------------------------------------------
        if self.display_analysis:
            fig_subplot.show()

    def MarkTendencia(
        lista, listaTempo, listaMin, tamanhoV, deslV, color, linewidth=1, alpha=0.95
    ):

        aberto = 0
        y = min(listaMin)
        for i in range(len(listaTempo)):
            if i >= 1:
                if (lista[i] == 1 and i == 1) or (
                    lista[i] == 1 and (lista[i - 1] == 0 or lista[i - 1] == -1)
                ):
                    aberto = 1
                    inicio = lista_tempo_number[i - 1]
                    # vinicio = lista_minimo[i]
                if aberto == 1 and (
                    (lista[i] == 0 and lista[i - 1] ==
                     1) or (i == len(listaTempo) - 1)
                ):
                    fim = lista_tempo_number[i - 1]
                    # vfim = lista_minimo[i]
                    aberto = 0
                    rect = patches.Rectangle(
                        (inicio, y - deslV),
                        fim - inicio,
                        y * tamanhoV,
                        linewidth=linewidth,
                        edgecolor=color,
                        facecolor=color,
                        alpha=alpha,
                    )
                    ax.add_patch(rect)
