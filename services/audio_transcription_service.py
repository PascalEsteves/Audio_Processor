from models.models import Audios_Transcriptions, Cutted_Audios
from services.api_comsumer_service import Api_Consumer
from typing import Dict, List

class Audio_Transcrioption(Api_Consumer):

    _service_name = "audio_transcription"

    def __init__(self,
                 database:object,
                 connector:object,
                 logger:object):

        super().__init__(endpoint="WHISPER")
        self._db = database
        self._con = connector
        self.logger = logger


    def _get_audios_to_transcribe(self)->List[Dict]:

        audio_to_transcribe : List[Dict[str]] = [{"id":f.id,
                                       "Filepath": f.Filepath}
                                      for f in self._db.get_all_from_model_with_status(model = Cutted_Audios, status=['Ready_To_Transcribe'])]

        return audio_to_transcribe

    def _add_data_to_database(self, audio_trancribed:List[object]):

        audio_data =[audio.__dict__ for audio in audio_trancribed]
        self._db.add_data_to_db(model=Audios_Transcriptions, data=audio_data)
        self._db.update_status(model= Cutted_Audios, id_list= [f.get("id") for f in audio_data], status_list=['Transcribed']*len(audio_data))

    def run_transcription(self):

        audios_to_transcribe :Dict[str, Dict[str, str]] = self._get_audios_to_transcribe()

        if audios_to_transcribe:

            audio_trancribed :List = []
            for audio in audios_to_transcribe:

                try:
                    result : Dict = self.transcribe_audio(self._con.get_public_link(audio.get("Filepath")), audio_id=audio.get("id"))
                    audio_trancribed.extend(Audios_Transcriptions(**result))

                except Exception as e:
                    print(f"Error {str(e)}")

            if audio_trancribed:
                self._add_data_to_database(audio_trancribed=audio_trancribed)

        else:
            self.logger.info("No new audio to ingest")








