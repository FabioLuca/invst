from jinja2 import Template, Environment, FileSystemLoader
from datetime import datetime, timedelta, date
import numpy as np
import pandas as pd
import json
from pathlib import Path


class MailFormatter:

    def create_agenda(self, dataframe: pd.DataFrame):
        """Creates a calendar-like table to be displayed on the report (e-mail).
        The calendar table is populated with the events from the day and any
        predictions available for the next days.

        The analysis methods to be displyes in thei calendar can be filtered by
        using the parameter ``filter_in_analysis`` from the configuration file.
        """

        date_today = datetime.today()
        date_today = date_today.replace(
            hour=0, minute=0, second=0, microsecond=0)

        list_events = []
        list_days = []

        # ----------------------------------------------------------------------
        #   Filter in the chosen methods to be displayed.
        # ----------------------------------------------------------------------
        dataframe = dataframe[dataframe['Method'].isin(
            self.config.filter_in_analysis)]

        # ----------------------------------------------------------------------
        #   Builds the calendar dates and key parameters.
        # ----------------------------------------------------------------------
        dates = pd.to_datetime(dataframe["Day Next Event"], errors="coerce")
        max_date = dates.max()
        first_weekday = date_today.weekday()
        delta = max_date - date_today
        total_range = delta.days
        if pd.isnull(max_date):
            total_range = 1
        if total_range < 20:
            total_range = 20
        first_week_spam = 7 - first_weekday
        remaining = total_range - first_week_spam
        count_weeks_middle = int(remaining // 7)
        last_week_spam = (remaining % 7) + 1

        weekdays = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

        # ----------------------------------------------------------------------
        #   Creates the first week in the calendar.
        # ----------------------------------------------------------------------
        week_dict = {}
        i = 0
        for day in weekdays:
            date_entry = date_today + timedelta(days=(i-first_weekday))
            week_dict[day] = {"day": date_entry.strftime('%Y.%m.%d'),
                              "info": [],
                              "today": False}
            if i-first_weekday == 0:
                week_dict[day]["today"] = True
            i = i + 1
        list_days.append(week_dict)

        # ----------------------------------------------------------------------
        #   Creates the middle weeks in the calendar.
        # ----------------------------------------------------------------------
        for j in range(0, count_weeks_middle + 1):
            week_dict = {}
            i = 0
            for day in weekdays:
                date_entry = date_entry + timedelta(days=1)
                week_dict[day] = {"day": date_entry.strftime('%Y.%m.%d'),
                                  "info": [],
                                  "today": False}
                i = i + 1
            list_days.append(week_dict)

        # ----------------------------------------------------------------------
        #   Add the events to the calendar.
        # ----------------------------------------------------------------------
        for index, row in dataframe.iterrows():

            if row["Last Day Event"] != "HOLD":
                event_date = date_today
                weekday_event = event_date.weekday()
                event = {"date": event_date,
                         "weekday": weekday_event,
                         "symbol": row["Symbol"],
                         "event": row["Last Day Event"],
                         "type": "standard",
                         "summary": f"{row['Symbol']}: {row['Last Day Event']} ({row['Method']})"
                         }
                k, day = self.find_element(list_days, "day", event_date)
                list_days[k][day]["info"].append(event)

            if row["Next Event"] != "HOLD":
                event_date = datetime.strptime(
                    row["Day Next Event"], '%Y-%m-%d')
                weekday_event = event_date.weekday()
                event = {"date": event_date,
                         "weekday": weekday_event,
                         "symbol": row["Symbol"],
                         "event": row["Next Event"],
                         "type": "prediction",
                         "summary": f"{row['Symbol']}: {row['Next Event']} ({row['Method']}-predic.)"
                         }
                k, day = self.find_element(list_days, "day", event_date)
                list_days[k][day]["info"].append(event)

        return list_events, list_days

    def create_stats(self, stats: dict):

        list_parameters = {}
        list_status = []

        dict_parameters = stats["parameters"]
        dict_status = stats["execution"]

        for group in dict_parameters:
            list_item_parameter = []
            params = dict_parameters[group]
            for param in params:
                item = params[param]
                if isinstance(item["value"], list):
                    value_display = ', '.join([str(elem)
                                               for elem in item["value"]])
                else:
                    value_display = item["value"]

                if "unit" in item:
                    if item["unit"] != "unitless" and item["unit"] != "":
                        new_item = f"{param}: {value_display} {item['unit']}"
                    else:
                        new_item = f"{param}: {value_display}"
                else:
                    new_item = f"{param}: {value_display}"

                list_item_parameter.append(new_item)
            list_parameters[group] = list_item_parameter

        list_status = dict_status
        str_symbols = ""
        symbols = list_status["Symbols"]
        for symbol in symbols:
            str_symbols = str_symbols + \
                f"<b>{symbol['symbol']}</b>: {symbol['name']}\n<br>"

        list_status["Symbols"] = str_symbols

        list_status["Duration"] = f"{list_status['Duration']:.2f} minutes"

        return list_parameters, list_status

    def find_element(self, list, key, value):
        for i, dict in enumerate(list):
            list_week = dict.keys()
            for day in list_week:
                if dict[day][key] == value.strftime('%Y.%m.%d'):
                    return i, day
        return -1, -1

    def format_email_fail_empty(self):

        time_str = datetime.now().strftime('%y.%m.%d %H:%M:%S')
        subject = f"""FAIL: Completed analysis of tickers ({time_str})"""
        body_html = f"""Completed analysis of tickers with a failure: The list
                        of results was empty, meaning no analysis was possible.
                        \nReference: {time_str}"""

        return subject, body_html

    def format_email_success(self,
                             results: pd.DataFrame,
                             execution_stat: dict,
                             save_html: bool = True):

        columns_order = ["Symbol",
                         "Method",
                         "Analysis length",
                         "Average Volume",
                         "Up Movement",
                         "Down Movement",
                         "Ratio Movement",
                         "Last Day Event",
                         "Previous Day Event",
                         "Next Event",
                         "Day Next Event",
                         "Relative gain",
                         "Relative gain reference",
                         "Relative gain comparison"]

        results_html = results.to_html(
            classes='results',
            index=False,
            columns=columns_order,
            float_format='{:10.2f}'.format)

        list_events, list_days = self.create_agenda(
            dataframe=results)

        list_parameters, list_status = self.create_stats(stats=execution_stat)

        time_str = datetime.now().strftime('%y.%m.%d %H:%M:%S')

        template_file = Path.cwd().resolve() / "src" / \
            "lib" / "communication" / "mail_templates"
        env = Environment(loader=FileSystemLoader(template_file),
                          trim_blocks=True)

        body_html = env.get_template("success_mail.j2").render(
            value_timestamp=time_str,
            dataframe_html=results_html,
            agenda_days=list_days,
            parameters=list_parameters,
            statistics=list_status)

        if save_html:
            text_file = open("content.html", "w")
            n = text_file.write(body_html)
            text_file.close()

        subject = f"""SUCCESS: Completed analysis of tickers ({datetime.now().strftime('%y.%m.%d %H:%M:%S')})"""

        return subject, body_html
