import os
from dataclasses import dataclass
from configs.configs import ProcessorConfig
from sql.database import Database, Config
from connector import BoxConnector, BlobStorageConnector,S3_Connector
from services.service_manager import ServiceManager
from logs.logger import DualLogger


class Audio_Processer:

    def __init__(self) -> None:
        self._config = ProcessorConfig(config_filepath=os.getenv("CONFIG_PATH"))
        self.connector = self._data_connector()
        self.logger = DualLogger()
        self.connect_to_db()
        self.register_services()

    def _data_connector(self)->object:

        """
        Return Connector to Storage
        """

        connector : str = self._config.processor
        path: str = self._config.datasource

        if connector == 'S3':
            return S3_Connector()
        elif connector == 'BLOB':
            return BlobStorageConnector()
        elif connector == 'BOX':
            return BoxConnector()
        else:
            raise Exception("Processor not Implemented")

    def connect_to_db(self):
        """
        Connect to SQL DataBase
        :param sql_server:  server to connect to
        :param DB_HOST: database Host
        :param DB_NAME: Database Name
        :param DB_USERNAME: Username used to connect
        :param DB_PASSWORD: Password used to login
        :param active_directory: if db login is done using AAD..
        """
        config:object = Config(engine=self._config.engine)
        self._db = Database(config=config)

    @property
    def database(self):
        """
        returns the SqlAlchemny-based Database object
        """
        return self._db

    def register_services(self):

        self.services = ServiceManager(database = self._db,
                                       connector = self.connector,
                                       logger = self.logger)

        audio_ingestion = self.services.audio_ingestion
        if audio_ingestion:
            self.audio_ingestion = audio_ingestion.run_ingestion

        speech_recognition = self.services.speach_recognition
        if speech_recognition:
            self.speech_recognition = speech_recognition.run_segmentation

        audio_cutter = self.services.audio_cutter
        if audio_cutter:
            self.cut_audios = audio_cutter.run_cut_audios

        audio_transcription =self.services.audio_tramscription
        if audio_transcription:
            self.audio_transcription = audio_transcription.run_transcription








