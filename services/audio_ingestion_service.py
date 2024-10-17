from models.models import AudioCollection
from typing import List
from sql.database import Database


class Audio_Ingestion:

    _service_name = "audio_ingestion"

    def __init__(self, database:Database, connector: object, logger:object):

        self._db = database
        self._con = connector
        self.logger = logger
        self.extensions = (".mp3",".wav")

    def _get_all_data_ingested(self):
        """
        Return all files ingested in DB
        """
        audio_ingested : List =[f.Audio_path for f in self._db.get_all_from_model(model= AudioCollection)]
        return audio_ingested

    def _get_files_in_storage(self, folder:str=None, container:str=None):
        """
        Returns all files in storage
        """
        return self._con.get_list_files(container=container, folder=folder)

    def _remove_files_ingested(self, ingested_files:List, total_files:List)->List:
        """
        Returns List of files not ingested
        """
        new_files :List = [f for f in total_files if f not in ingested_files]
        return new_files

    def _add_data_to_database(self, new_ingestion:List[object]):

        audio_data =[audio.__dict__ for audio in new_ingestion]
        self._db.add_data_to_db(model=AudioCollection, data=audio_data)

    def run_ingestion(self, folder:str=None, container:str=None):

        files_ingested : List = self._get_all_data_ingested()
        files_in_storage : List = [f for f in self._get_files_in_storage(folder=folder, container=container) if f.endswith(self.extensions)]
        new_files : List = self._remove_files_ingested(ingested_files=files_ingested, total_files=files_in_storage)

        if new_files:
            new_ingestion = []
            for new_audio in new_files:
                new_ingestion.append(AudioCollection(Filepath=new_audio))

            self._add_data_to_database(new_ingestion)

        else:
            print("No Data To Ingest")














