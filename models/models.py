from sqlalchemy import Column, String,ForeignKey,Float,Integer,create_engine
import os
from sqlalchemy.orm import declarative_base
from sql.database import Config
from environments.environments import Environments

EntityDboBase = declarative_base()

class AudioCollection(EntityDboBase):

    __tablename__ = 'audio_collection'

    id = Column(Integer, primary_key = True)
    Filepath = Column(String, unique=True)
    Audio_name= Column(String)
    Date = Column(String)
    Comments = Column(String)
    Status = Column(String)

    def __init__(self, Filepath:str) -> None:

        self.Filepath = Filepath
        self.Audio_name = self._get_audio_name()
        self.Date= self._get_submission_date()
        self.Comments = "NA"
        self.Status = "Ingested"

    def _get_audio_name(self)->str:
        return os.path.split(self.Filepath)[-1]

    def _get_submission_date(self)->str:
        return self.Filepath.split("/")[1]

    def __str__(self):
        return f"Audio name : {self.Audio_name} located in {os.path.split(self.Filepath)[-1]} was ingeted in {self.Date} by {self.Storage}"

class Audio_Segments(EntityDboBase):

    __tablename__ = 'audio_segments'

    id = Column(Integer, primary_key = True)
    Audio_id = Column(Integer, ForeignKey('audio_collection.id'))
    Segment_number = Column(String)
    Start_time = Column(Float)
    End_time = Column(Float)
    Status = Column(String)

    def __init__(self, Audio_id:int, Segment_number:str, Start_time:float, End_time:float) -> None:

        self.Audio_id = Audio_id
        self.Segment_number = Segment_number
        self.Start_time = Start_time
        self.End_time= End_time
        self.Status = "Ready_To_Cutted"

class Cutted_Audios(EntityDboBase):

    __tablename__ = 'audios_cutted'

    id = Column(Integer, primary_key = True)
    Audio_id = Column(Integer, ForeignKey('audio_collection.id'))
    Segment_id = Column(Integer, ForeignKey('audio_segments.id'))
    Filepath = Column(String, unique=True)
    Start_time = Column(Float)
    End_time = Column(Float)
    Status = Column(String)

    def __init__(self,
                 Audio_id:int,
                 Segment_id: int,
                 Filepath:str,
                 Start_time:float,
                 End_time:float) -> None:

        self.Audio_id = Audio_id
        self.Segment_id = Segment_id
        self.Filepath = Filepath
        self.Start_time = Start_time
        self.End_time= End_time
        self.Status = "Ready_To_Transcribe"

class Audios_Transcriptions(EntityDboBase):

    __tablename__ = 'audios_transcriptions'

    id = Column(Integer, primary_key = True)
    Audio_id = Column(Integer, ForeignKey('audios_cutted.id'))
    Transcription = Column(String)
    Status = Column(String)

    def __init__(self, audio_id:int, transcription:str) -> None:
        self.Audio_id = audio_id
        self.Transcription = transcription
        self.Status = "Ingested"

config = Config(engine=Environments.get_db_engine())

engine = create_engine(config.get_connection_string())
EntityDboBase.metadata.create_all(bind=engine)

