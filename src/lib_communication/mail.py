import requests


class Mail:

    def send_email(self, subject: str,
                   body_html: str, body_plain: str = ""):
        """Sends an email using the MailGun API.
        """
        url = self.access_config["email"]["URL_BASE"] + \
            self.access_userdata["email"]["DOMAIN"] + \
            self.access_config["email"]["URL_MESSAGE"]

        apikey = self.access_userdata["email"]["APIKEY"]

        to_email = self.access_userdata["email"]["to_email"]
        from_email = self.access_userdata["email"]["from_email"]

        try:
            # disable ssl warning
            # requests.packages.urllib3.disable_warnings()
            # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            # context.verify_mode = ssl.CERT_NONE

            r = requests.post(url,
                              auth=("api", apikey),
                              data={"from": from_email,
                                    "to": to_email,
                                    "subject": subject,
                                    "html": body_html,
                                    "text": body_plain})

        except Exception as e:
            # status, msg, result = Log.Registro("Erro ao requisitar MailGun: " +
            #                                    str(e), exception=str(e),
            #                                    level=3, nome=__name__)
            return False, "Falha ao acessar MailGun", str(e)
        if r.status_code == 200:
            # Log.Registro(texto="Envio do email com sucesso",
            #              level=1, nome=__name__)
            return True, "OK", r.status_code
        else:
            # Log.Registro(texto="Falha no envio de email: " + r.status_code,
            #              level=3, nome=__name__)
            return False, "Falha no envio de email", r.status_code
