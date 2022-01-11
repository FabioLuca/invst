import dropbox
from pathlib import Path
import requests


class DropboxAPI:

    def connect_oauth(self):

        app_key = self.app_key
        app_secret = self.app_secret

        # build the authorization URL:
        authorization_url = "https://www.dropbox.com/oauth2/authorize?client_id=%s&response_type=code" % app_key

        # send the user to the authorization URL:
        print('Go to the following URL and allow access:')
        print(authorization_url)

        # get the authorization code from the user:
        # raw_input('Enter the code:\n')
        authorization_code = ""

        # exchange the authorization code for an access token:
        token_url = "https://api.dropboxapi.com/oauth2/token"
        params = {
            "code": authorization_code,
            "grant_type": "authorization_code",
            "client_id": app_key,
            "client_secret": app_secret
        }
        r = requests.post(token_url, data=params)
        print(r.text)

    def upload_file(self, file: Path, destination_folder: str):
        """upload a file to Dropbox using API v2
        """
        self.logger.info(f"Copying file to Dropbox: {file.name}")

        dbx = dropbox.Dropbox(self.access_token)

        if destination_folder[0] != "/":
            destination_folder = "/" + destination_folder

        if destination_folder[-1] != "/":
            destination_folder = destination_folder + "/"

        destination = destination_folder + str(file.name)
        try:
            account = dbx.users_get_current_account()
        except dropbox.exceptions.AuthError as err:
            self.logger.error("Error authenticating to Dropbox.")
            return None

        try:
            with open(file, 'rb') as f:
                response = dbx.files_upload(f.read(),
                                            destination,
                                            mode=dropbox.files.WriteMode.overwrite)
        except dropbox.exceptions.ApiError as err:
            self.logger.error(f"Error in the Dropbox API: {err}")
            return None

        return response
