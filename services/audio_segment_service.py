from models.models import Audio_Segments, AudioCollection
from services.api_comsumer_service import Api_Consumer
from typing import List, Dict
import os

class Audio_Segment(Api_Consumer):

    _service_name = "speach_recognition"

    def __init__(self,
                 database:object,
                 connector:object,
                 logger:object) -> None:

        super().__init__(endpoint="PYANNOTATE")
        self._db = database
        self._con = connector
        self.logger = logger

    def _get_audios_to_segment(self)->List[Dict] :

        audio_to_segment :List[Dict[str]] =[{
                               "Audio_id": f.id,
                               "Audio_name":f.Audio_name,
                               "Filepath": f.Filepath} for f in self._db.get_all_from_model_with_status(model = AudioCollection, status=['Ingested'])]

        return audio_to_segment

    def _add_data_to_database(self, audio_segmented:List[object]):

        audio_data =[audio.__dict__ for audio in audio_segmented]
        self._db.add_data_to_db(model=Audio_Segments, data=audio_data)
        self._db.update_status(model= AudioCollection, id_list= [f.get("Audio_id") for f in audio_data], status_list=['Segmented']*len(audio_data))

    def run_segmentation(self):

        audios_to_segment :List[Dict[str]] = self._get_audios_to_segment()

        if audios_to_segment:

            audio_segmented :List = []
            for audio in audios_to_segment:

                try:
                    sas_link : str = self._con.get_public_link(audio.get("Filepath"))
                    results = self.get_audio_segments(sas_link, audio_id=audio.get("Audio_id"))
                    for result in results:
                        audio_segmented.append(Audio_Segments(**result))

                except Exception as e:
                    print(f"Error {str(e)}")

            if audio_segmented:
                self._add_data_to_database(audio_segmented=audio_segmented)

        else:
            self.logger.info("No new audio to segment")

