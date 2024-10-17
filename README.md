# Audio Pipeline Solution for Ingest, Segment, Cut and Transribe

##### Requirements 
- Hugging Face Token
- Api endpoint for pyannote and whisper
- Select The Storage required ( Blob, Box or S3)

##### Step 1
#
```cmd
git clone https://github.com/PascalEsteves/Audio_Processor.git 
``` 

##### Step 2
#
```cmd
python -m venv .venv
``` 
##### Step 3
#
###### Ativate virtual env
#
```cmd
pip install -r requirements.txt
``` 
##### Step 4
###### - Create .env file and add required fields
#
    - BLOB STORAGE / BOX / S3 Connection strings
    - Path to config.json file where you need to identify the PROCESSOR{BLOB/BOX/S3}/DATASOURCE(Folder with audios in storage)/ENGINE(Database required sqlite3/Postgres/Mysql)
    - CONTAINER IF BLOB
    - DB INFO
    - HUGGING FACE TOKEN
 
#
##### Step 5
# 

```python
from audio_processor import Audio_Processer

pipeline = Audio_Processer()
pipeline.audio_ingestion() # Audio Ingestion and Map in db
pipeline.speech_recognition() # Audio Activity Identification 
pipeline.cut_audios()  # Audio Cutter - Cut Speech segments
pipeline.audio_transcription()  # Audio Cutter - Cut Speech segments
``` 
    
Autor: Pascal Esteves
