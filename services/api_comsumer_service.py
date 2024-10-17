from json import JSONDecodeError
from environments.environments import Environments
import requests

class Api_Consumer:

    def __init__(self, endpoint:str):
        self._base_url = Environments.get_api_endpoint(endpoint=endpoint)
        self.API_KEY = Environments.get_hugging_face_token()

    def get_audio_segments(self, public_link:str, audio_id:int):

        path : str = "/audio_segmentation"
        payload = {"audio_url": public_link,
                   "audio_id": audio_id}

        return self.request("GET", path=path, payload=payload)

    def transcribe_audio(self, public_link:str, audio_id:int):

        path : str = "/transcription"
        payload = {"audio_url": public_link,
                   "audio_id": audio_id}

        return self.request("GET", path=path, payload=payload)

    def request(self, request_type, path, payload):

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.API_KEY}"
        }

        if payload:
            response = requests.request(request_type, self._base_url + path, headers=headers, json=payload)
        else:
            response =requests.request(request_type, self._base_url + path, headers=headers)
        try:
            return response.json()
        except JSONDecodeError:
            return response.text