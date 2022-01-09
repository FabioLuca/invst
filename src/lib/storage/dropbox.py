import dropbox


class Dropbox:

    def connect(self):
        dbx = dropbox.Dropbox(self.access_token)
        result = dbx.files_list_folder(path="")
        print(result)

    def upload_file(self, file_from, file_to):
        """upload a file to Dropbox using API v2
        """
        dbx = dropbox.Dropbox(self.access_token)

        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to)
