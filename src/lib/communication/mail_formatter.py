from jinja2 import Template, Environment, FileSystemLoader
from datetime import datetime
import pandas as pd
from pathlib import Path


class MailFormatter:

    def format_email_fail_empty(self):

        time_str = datetime.now().strftime('%y.%m.%d %H:%M:%S')
        subject = f"""FAIL: Completed analysis of tickers ({time_str})"""
        body_html = f"""Completed analysis of tickers with a failure: The list
                        of results was empty, meaning no analysis was possible.
                        \nReference: {time_str}"""

        return subject, body_html

    def format_email_success(self, results: pd.DataFrame):

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

        time_str = datetime.now().strftime('%y.%m.%d %H:%M:%S')

        template_file = Path.cwd().resolve() / "src" / \
            "lib" / "communication" / "mail_templates"
        env = Environment(loader=FileSystemLoader(template_file),
                          trim_blocks=True)

        body_html = env.get_template("success_mail.j2").render(
            value_timestamp=time_str,
            dataframe_html=results_html)

        subject = f"""SUCCESS: Completed analysis of tickers ({datetime.now().strftime('%y.%m.%d %H:%M:%S')})"""

        return subject, body_html
