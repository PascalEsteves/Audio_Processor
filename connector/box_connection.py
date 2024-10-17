import os
from typing import List
import boxsdk
from boxsdk.object.item import Item
from collections.abc import Iterable
from environments.environments import Environments

class BoxConnector:

    __connector_name__ = "Box Storage"

    def __init__(
        self,
        jwt_auth: boxsdk.JWTAuth = None,
    ) -> None:
        self.auth = Environments.get_box_token()
        self.client = self._build_client()


    def _build_client(self):
        return boxsdk.Client(self.auth)

    @classmethod
    def from_jwt_file(cls: object, jwt_file_path: str)->object:
        """
        Initialize Box client using a JWT file
        :param jwt_file_path: filepath of the JWT file needed for authentication
        :type  jwt_file_path: str
        :return: Box Connection
        """
        assert os.path.isfile(jwt_file_path)

        auth :dict = boxsdk.JWTAuth.from_settings_file(jwt_file_path)
        return cls(jwt_auth=auth)

    def search_for_item(
        self,
        name: str,
        name_exact_match: bool = False,
        enforce_single_result: bool = False,
        limit: int = None,
        result_type: str = None,
        file_extensions: List[str] = None,
        **kwargs,
    ) -> List[Item]:
        """
        Search for an item on Box
        :param name: name of the item to search for
        :type  name: str
        :param result_type: designate if searching for a file or folder, limited to ['file', 'folder']
        :type limit: int
        :param exact_match: restrict the search to exact string matches for file_name
        :type blob_new_name: bool
        :param enforce_single_result: raise exception if name returns multiple matches
        :type enforce_single_result: bool
        :param limit: max number of items to return
        :type limit: int
        :return: List[boxsdk.object.item.Item]
        """
        if result_type:
            assert result_type.strip().lower() in ["file", "folder"]

        result = list(
            self.client.search().query(
                query=name if not name_exact_match else f'"{name}"',
                limit=limit,
                result_type=result_type,
                file_extensions=file_extensions,
                **kwargs,
            )
        )

        if enforce_single_result and len(result) > 1:
            matches = [x for x in result if x.name == name]
            if len(matches) > 1:
                raise ValueError(
                    f"Ambiguous item name '{name}', multiple results found: {matches}"
                )
            return matches

        return result

    def search_for_file(
        self,
        file_name: str,
        parent_folder: str = None,
        file_extensions: List[str] = None,
        exact_match: bool = False,
        enforce_single_result: bool = False,
    )->List:
        """
        Search for a file on Box
        :param file_name: name of the file to search for
        :param parent_folder: (optional) name of Box folder to limit the search to
        :param file_extensions: (optional) list of specific file extensions to search against
        :param exact_match: restrict the search to exact string matches for file_name
        :param enforce_single_result: raise exception if name returns multiple matches
        :return: List[boxsdk.object.item.Item]
        """
        ancestor_folder = []

        if parent_folder:
            folder = self.search_for_folder(
                parent_folder, exact_match=True, enforce_single_result=True
            )[0]
            ancestor_folder.append(folder)

        files = list(
            self.search_for_item(
                file_name,
                name_exact_match=exact_match,
                result_type="file",
                enforce_single_result=enforce_single_result,
                file_extensions=file_extensions,
                ancestor_folders=ancestor_folder,
            )
        )

        return files

    def search_for_folder(
        self,
        folder_name,
        exact_match: bool = False,
        enforce_single_result: bool = False,
    ):
        """
        Search for a file on Box
        :param folder_name: name of the file to search for
        :type  folder_name: str
        :param exact_match: restrict the search to exact string matches for file_name
        :type blob_new_name: bool
        :param enforce_single_result: raise exception if name returns multiple matches
        :type enforce_single_result: bool
        :return: List[boxsdk.object.item.Item]
        """
        folders = list(
            self.search_for_item(
                folder_name,
                result_type="folder",
                name_exact_match=exact_match,
                enforce_single_result=enforce_single_result,
            )
        )
        return folders

    def upload_file(self, filepath:str, filename:str, folder_name:str):

        """
        Upload a file to a given Box folder.
        :param filepath: local filepath of the data to upload
        :param folder_name: Name of Box folder to upload into
        :param filename: Name to assign to file on upload
        :return: None
        """
        try:
            folder_search = self.search_for_folder(folder_name, exact_match=True, enforce_single_result=True)
            target_folder = self.client.folder(folder_search[0].id)
            uploaded_file = target_folder.upload(filepath, file_name=filename)
        except Exception as e:
            print(f"Error {str(e)}")

    def download_file(self,
                      folder_name: str,
                      filename: str,
                      filepath: str):
        """
        Downloads a file to a given path.
        :param folder_name: Name of Box folder that contains the file
        :param blob_name: Name of blob to get from the folder
        :param filepath: Name of local file to be generated
        """
        files = self.search_for_file(
            filename, folder_name, exact_match=True, enforce_single_result=True
        )

        with open(filepath, "wb") as of:
            files[0].download_to(of)

    def get_list_of_files(self,
                          folder_name,
                          include_folders: bool = False,
                            **kwargs
                    ) -> List[Item]:
        """
        List all the files stored in a Box folder

        :param folder_name: name of Box folder
        :param include_folders: return sub-folders
        :return: List[boxsdk.object.item.Item]
        """
        folder = self.search_for_folder(
            folder_name=folder_name, exact_match=True, enforce_single_result=True
        )[0]

        files : List[Item] = [
            x
            for x in folder.get_items()
            if (x.object_type != "folder" and not include_folders) or include_folders
        ]

        return files

    def generate_public_link(self,
                              folder_name: str,
                              filename: str):

        files = self.search_for_file(
            folder_name, filename, exact_match=True, enforce_single_result=True
        )
        url = files[0].get_download_url()
        return url


