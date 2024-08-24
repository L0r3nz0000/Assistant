from markdown import remove_markdown
from sound import Sound
import requests
import base64
import os

endpoint = "https://audio.api.speechify.com/generateAudioFiles"

def _text_to_audio(text):
  text = remove_markdown(text)
  json = {
    "audioFormat": "mp3",
    "paragraphChunks": [
      text
    ],
    "voiceParams": {
      "engine": "azure",
      "languageCode": "it-IT",
      "name": "palmira"
    }
  }

  r = requests.post(endpoint, json=json)

  if "audioStream" not in r.json():
    return
  
  audioStream_b64 = r.json()['audioStream']

  mp3_bytes = base64.b64decode(audioStream_b64)
  output_file_name = "sounds/output.mp3"

  with open(output_file_name, "wb") as output_file:
    output_file.write(mp3_bytes)
  return output_file_name

def speak(text):
  filename = _text_to_audio(text)

  s = Sound(filename, speed=1.1)
  s.play()