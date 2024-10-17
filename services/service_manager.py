from typing import Any, ClassVar, Dict, List, Optional
from services.audio_ingestion_service import Audio_Ingestion
from services.audio_cutter_service import Audio_Cutter
from services.audio_segment_service import Audio_Segment
from services.audio_transcription_service import Audio_Transcrioption


class ServiceManager:

    def __init__(self, **kwargs:Any):
        self.logger = kwargs.get("logger")
        self._services : Dict[str, Optional[object]] = {}
        self.setup_services(**kwargs)

    def setup_services(self, **kwargs):

        self.audio_ingestion = self.setup_service(
                                                  cls=Audio_Ingestion,
                                                  database = kwargs.get("database"),
                                                  connector = kwargs.get("connector"),
                                                  logger= self.logger
                                                  )
        self._services["audio_ingestion"] = self.audio_ingestion

        self.speach_recognition = self.setup_service(
                                                        cls=Audio_Segment,
                                                        database = kwargs.get("database"),
                                                        connector = kwargs.get("connector"),
                                                        logger = self.logger
                                                    )
        self._services["speach_recognition"] = self.speach_recognition

        self.audio_cutter = self.setup_service(
                                                  cls=Audio_Cutter,
                                                  database = kwargs.get("database"),
                                                  connector = kwargs.get("connector"),
                                                  logger = self.logger
                                                  )
        self._services["audio_cutter"] = self.audio_cutter

        self.audio_tramscription = self.setup_service(
                                                  cls=Audio_Transcrioption,
                                                  database = kwargs.get("database"),
                                                  connector = kwargs.get("connector"),
                                                  logger = self.logger
                                                  )
        self._services["audio_transcription"] = self.audio_tramscription

    def setup_service(self,
                      cls: object,
                      **kwargs:Any):
        """Setup a service instance."""

        try:
            return cls(
                **kwargs,
            )
        except Exception as e:
            self.logger.warning(
                f"Failed to create service: {cls._service_name}"
            )
            self.logger.warning(e)

        return None

    def get(self, service_name: str) -> Optional[object]:
        return self._services.get(service_name)

    def list_services(self) -> List[str]:
        return list(self._services.keys())



