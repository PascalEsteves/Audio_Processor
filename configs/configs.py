from typing import List, Dict, Tuple
import os
import json
from dataclasses import dataclass


class Config(object):

    def __init__(self,
                 configs:object,
                 required_attri:List) -> None:

        self._config= configs
        valid, missing = self._valid_config(required_attri)

        if not valid:
            raise ValueError(f"Missing required attributes: {missing}")

    def _get_property(self, property_name:str, default=None)->str:
        return self._config.get(property_name, default)

    def _valid_config(self, required_attri:List):
        missing : List =  [x for x in required_attri if self._get_property(x) == None]
        valid: bool = all(field in self._config for field in required_attri)
        return valid, missing

class FileConfig(Config):

    def __init__(self, filepath: str, required_attri: List) -> None:

        assert os.path.exists(filepath), FileNotFoundError(filepath)

        with open(filepath, "r", encoding='utf-8') as f:
            configs = json.load(f)

        super().__init__(configs, required_attri)

class ProcessorConfig(FileConfig):

    REQUIRED_COLUMNS = ["PROCESSOR", "DATASOURCE", "ENGINE"]
    PROCESSOR_AVAILABLE = ["S3","BLOB", "BOX"]
    ENGINE_AVAILABLE = ["postgres","mssql","sqlserver","sqlite"]

    @property
    def processor(self):
        return self._get_property("PROCESSOR")

    @property
    def datasource(self):
        return self._get_property("DATASOURCE")

    @property
    def engine(self):
        return self._get_property("ENGINE")

    def __init__(self, config_filepath:str):
        super().__init__(filepath=config_filepath, required_attri=ProcessorConfig.REQUIRED_COLUMNS)

        if self._get_property("PROCESSOR") not in ProcessorConfig.PROCESSOR_AVAILABLE:
            raise Exception("Processor Not Available")

        if self._get_property("ENGINE") not in ProcessorConfig.ENGINE_AVAILABLE:
            raise Exception(f"Connector to {0} not Available".format(self._get_property("ENGINE")))