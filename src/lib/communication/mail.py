import requests
from pathlib import Path
from src.lib import messages as M


class Mail:

    def send_email(self, subject: str,
                   body_html: str,
                   body_plain: str = "",
                   attachment: list[Path] = None):
        """Sends an email using the MailGun API.
        """
        url = self.access_config["email"]["URL_BASE"] + \
            self.access_userdata["email"]["DOMAIN"] + \
            self.access_config["email"]["URL_MESSAGE"]

        apikey = self.access_userdata["email"]["APIKEY"]

        to_email = self.access_userdata["email"]["to_email"]
        from_email = self.access_userdata["email"]["from_email"]

        if attachment is not None:
            if isinstance(attachment, Path):
                attachment = [attachment]
            attachment_request = []
            for item in attachment:
                if item.exists():
                    outfile = open(item, 'rb').read()
                    attachment_request.append(
                        ("attachment", (item.name, outfile)))
        else:
            attachment_request = None

        try:
            # disable ssl warning
            # requests.packages.urllib3.disable_warnings()
            # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            # context.verify_mode = ssl.CERT_NONE
            r = requests.post(url,
                              auth=("api", apikey),
                              files=attachment_request,
                              data={"from": from_email,
                                    "to": to_email,
                                    "subject": subject,
                                    "html": body_html,
                                    "text": body_plain})

        except Exception as e:
            result = str(e)
            flag, level, message = M.get_status(self.logger_name,
                                                "Comm_SendEmail_API_Fail")

        if r.status_code == 200:
            result = r
            flag, level, message = M.get_status(self.logger_name,
                                                "Comm_SendEmail_Success")

        else:
            result = r
            flag, level, message = M.get_status(self.logger_name,
                                                "Comm_SendEmail_Fail")

        return result, flag, level, message
