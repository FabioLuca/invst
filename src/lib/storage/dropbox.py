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

    def fix_folder_path(self, folderpath: str):
        if folderpath == "":
            folderpath = "/"
        else:
            if folderpath[0] != "/":
                folderpath = "/" + folderpath
            if folderpath[-1] != "/":
                folderpath = folderpath + "/"

        return folderpath

    def list_files(self, folderpath: str, criteria: str = None):
        """List all files in a folder in Dropbox using API v2. This method will
        list only files direct in the specified Dropbox folder, and not in
        subdirectories.

        Parameters
        ----------
        folderpath : str
            String to the path in Dropbox. Part of the path is the default one
            set in the condfiguration files. This is the relative path from the
            configuration to the final location, as::

                <Configuration Path> / <destination_folder> /

            For example::

                <Configuration Path> = "/Export"
                <destination_folder> = "/Path/To/Files/"

                Result = "/Export/Path/To/Files/"

        criteria: str, optional
            Substring to be found in the filenames. If passed as ``None`` or
            not passed, then no filtering is applied.

        Returns
        -------
        list of strings
            Returns the list of files found in the folder, each one represented
            by a string. The files are sorted alphabetically.

        """
        self.logger.info(f"Listing files in the folder: {folderpath}")

        dbx = dropbox.Dropbox(self.access_token)

        folderpath = self.fix_folder_path(folderpath)

        folderpath = self.dropbox_path + folderpath

        result = dbx.files_list_folder(folderpath, recursive=False)

        list_files = []
        list_paths_display = []

        for entry in result.entries:
            # if isinstance(entry, dropbox.files.FolderMetadata):
            #     print(entry.id)
            if isinstance(entry, dropbox.files.FileMetadata):
                if entry.is_downloadable:
                    if criteria is not None:
                        if criteria in entry.name:
                            list_files.append(entry.name)
                            list_paths_display.append(entry.path_display)
                    else:
                        list_files.append(entry.name)
                        list_paths_display.append(entry.path_display)

        list_files.sort()

        return list_files

    def upload_file(self, file: Path, destination_folder: str):
        """Upload a file to Dropbox using API v2. The method will use the
        name of the file to be uploaded as the final name of the file in the
        destined location in Dropbox.

        Parameters
        ----------
        file : Path
            Path (pathlib) to the file to be uploaded.
        destination_folder: str
            String to the path in Dropbox. Part of the path is the default one
            set in the condfiguration files. This is the relative path from the
            configuration to the final location, as::

                <Configuration Path> / <destination_folder> / <file name>

            For example::

                <Configuration Path> = "/Export"
                <destination_folder> = "/Path/To/Files"
                <file name> = "Test-file.txt"

                Result = "/Export/Path/To/Files/Test-file.txt"

        Returns
        -------
        response
            Returns the Dropbox ``response`` is succesful or ``None`` if
            connection or access has failed.

        """
        self.logger.info(f"Uploading file to Dropbox: {file.name}")

        # ----------------------------------------------------------------------
        #   Connects to Dropbox and tests it.
        # ----------------------------------------------------------------------
        dbx = dropbox.Dropbox(self.access_token)
        try:
            account = dbx.users_get_current_account()
        except dropbox.exceptions.AuthError as err:
            self.logger.error("Error authenticating to Dropbox.")
            return None

        # ----------------------------------------------------------------------
        #   Prepares files names and paths.
        # ----------------------------------------------------------------------
        destination_folder = self.fix_folder_path(destination_folder)
        destination = destination_folder + str(file.name)

        # ----------------------------------------------------------------------
        #   Uploads the file to Dropbox.
        # ----------------------------------------------------------------------
        try:
            with open(file, 'rb') as f:
                response = dbx.files_upload(f.read(),
                                            destination,
                                            mode=dropbox.files.WriteMode.overwrite)
        except dropbox.exceptions.ApiError as err:
            self.logger.error(f"Error in the Dropbox API: {err}")
            return None

        return response

    def download_file(self, file: str, destination_folder: Path):
        """Download a file to Dropbox using API v2
        """

        self.logger.info(f"Downloading file from Dropbox: {file}")

        # ----------------------------------------------------------------------
        #   Prepares the name and path of the files for download.
        # ----------------------------------------------------------------------
        if self.dropbox_path is None:
            filepath = file
        else:
            if file[0] != "/":
                file = "/" + file
            filepath = self.dropbox_path + file

        filepath_elements = filepath.split("/")

        if destination_folder is None:
            destination_file = Path("/")
        else:
            destination_file = destination_folder
        for filepath_element in filepath_elements:
            if filepath_element != "":
                destination_file = destination_file / filepath_element

        # destination_file = Path.cwd().resolve() / destination_file

        destination_folder = destination_file.parents[0]

        if not destination_folder.exists():
            destination_folder.mkdir(parents=True, exist_ok=True)

        # ----------------------------------------------------------------------
        #   Connects to Dropbox and tests it.
        # ----------------------------------------------------------------------
        dbx = dropbox.Dropbox(self.access_token)

        try:
            account = dbx.users_get_current_account()
        except dropbox.exceptions.AuthError as err:
            self.logger.error("Error authenticating to Dropbox.")
            return None

        # ----------------------------------------------------------------------
        #   Downloads the file
        # ----------------------------------------------------------------------
        with open(destination_file, "wb") as f:
            metadata, response = dbx.files_download(path=filepath)
            f.write(response.content)

        return response

    def download_folder(self, folder: str = ""):

        folder = "/Models/lstm_MACD Histogram_IBM/"

        dbx = dropbox.Dropbox(self.access_token)

        result = dbx.files_list_folder(folder, recursive=True)

        folders = []

        def process_dirs(entries):
            for entry in entries:
                if isinstance(entry, dropbox.files.FolderMetadata):
                    folders.append(entry.path_lower + '--> ' + entry.id)

        process_dirs(result.entries)

        while result.has_more:
            result = dbx.files_list_folder_continue(result.cursor)
            process_dirs(result.entries)

        print(folders)

        return(folders)

    # , remote_path: str, local_path: Path):
