import dropbox
from pathlib import Path


class Dropbox:

    def connect(self):
        dbx = dropbox.Dropbox(self.access_token)
        result = dbx.files_list_folder(path="")

    def upload_file(self, file: Path, destination_folder: str):
        """upload a file to Dropbox using API v2
        """
        dbx = dropbox.Dropbox(self.access_token)

        if destination_folder[0] != "/":
            destination_folder = "/" + destination_folder

        if destination_folder[-1] != "/":
            destination_folder = destination_folder + "/"

        destination = destination_folder + str(file.name)

        with open(file, 'rb') as f:
            response = dbx.files_upload(f.read(), destination)

        return response
