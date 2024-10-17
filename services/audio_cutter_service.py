import librosa
from typing import List, Dict
from models.models import AudioCollection,Audio_Segments, Cutted_Audios
from multiprocessing.dummy import Pool as ThreadPool
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import os
import soundfile as sf
import json

class Audio_Cutter:

    _service_name = "audio_cutter"

    def __init__(self,
                 database:object,
                 connector: object,
                 logger: object) -> None:
        self._db = database
        self._con = connector
        self.logger = logger

    def _get_data_to_cut(self)->List[Dict]:

        audio_to_cut :List[Dict[str]] =[{
                               "id": f.id,
                               "Audio_name":f.Audio_name,
                               "Filepath": f.Filepath} for f in self._db.get_all_from_model_with_status(model = AudioCollection, status=['Segmented'])]

        return audio_to_cut

    def _get_segments_audios(self)->List[Dict]:

        segments_audios : List[Dict[str]] = [ { "Audio_id": f.Audio_id,
                                                "id": f.id,
                                                "Segment_number": f.Segment_number,
                                                "Start_time": f.Start_time,
                                                "End_time": f.End_time} for f in self._db.get_all_from_model_with_status(model = Audio_Segments, status=['Ready_To_Cutted'])]
        return segments_audios

    def _normalize_timestamp(self, timestamp: float, sampling_rate: int) -> float:
        return int(timestamp * sampling_rate)

    def _download_audio(self, audio_file):

        audio_filepath : str = audio_file.get("Filepath")
        audio_name : str = audio_file.get("Audio_name")

        self._con.download_file(audio_filepath,"audios/{0}".format(audio_name))

    def _upload_audio(self, audio_file):

        self._con.upload_file(audio_file.Filepath, audio_file.Filepath)

    def download_audios(self, audio_list:List)->None:

        with tqdm(total=len(audio_list), desc="Cut audios and upload them to blob") as pbar:
                with ThreadPoolExecutor(max_workers=8) as executor:
                    for error in executor.map(self._download_audio, audio_list):
                            if error:
                                print(error)
                            pbar.update()

    def upload_audios(self, audio_list:List)->None:

        with tqdm(total=len(audio_list), desc="Cut audios and upload them to blob") as pbar:
                with ThreadPoolExecutor(max_workers=8) as executor:
                    for error in executor.map(self._upload_audio, audio_list):
                            if error:
                                print(error)
                            pbar.update()

    def _cut_audios(self, audio_files:List, audio_segments:List)->List[object]:

        cutted_audios : List= []

        for audio in audio_files:
            time_series, sampling_rate = librosa.load(f"audios/{0}".format(audio.get("Audio_name")), sr=None, mono=False)
            time_series = librosa.to_mono(time_series)

            segments = [f for f in audio_segments if f.get("Audio_id")==audio.get('id')]
            for segm in segments:

                start_time = self._normalize_timestamp(segm.get("Start_time"), sampling_rate)
                end_time = self._normalize_timestamp(segm.get("End_time"), sampling_rate)

                try:
                    slot = time_series[:,start_time:end_time]
                except:
                    slot = time_series[start_time:end_time]

                slot = librosa.to_mono(slot)

                folder_name = segm.get('Audio_id')
                os.makedirs(f"cutted_audios/{folder_name}", exist_ok=True)
                output_file = f"cutted_audios/{folder_name}/{segm.get('Segment_number')}.wav"
                sf.write(output_file, slot.T, sampling_rate)

                cutted_audios.append(Cutted_Audios( Audio_id=segm.get('Audio_id'),
                                                    Segment_id=segm.get("id"),
                                                    Filepath=output_file,
                                                    Start_time=segm.get("Start_time"),
                                                    End_time=segm.get("End_time")))
        return cutted_audios

    def _add_data_to_database(self, cutted_audio:List[object]):

        audio_data =[audio.__dict__ for audio in cutted_audio]
        self._db.add_data_to_db(model=Cutted_Audios, data=audio_data)
        self._db.update_status(model= AudioCollection, id_list= [f.get("Audio_id") for f in audio_data], status_list=['Audio_Cutted']*len(audio_data))
        self._db.update_status(model= Audio_Segments,  id_list= [f.get("Segment_id") for f in audio_data], status_list=['Segment_Cutted']*len(audio_data))

    def run_cut_audios(self):

        data_to_cut : List[Dict[str]]  = self._get_data_to_cut()
        audio_segments : List[Dict[str]]  = self._get_segments_audios()

        if data_to_cut:

            self.download_audios(data_to_cut)
            cutted_audio = self._cut_audios(data_to_cut, audio_segments)

            self.upload_audios(cutted_audio)
            self._add_data_to_database(cutted_audio)

        else:
             self.logger.info("No more audios to cut")












