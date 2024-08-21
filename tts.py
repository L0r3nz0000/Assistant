from sound import Sound
import multiprocessing
import threading
import requests
import base64
import os

endpoint = "https://audio.api.speechify.com/generateAudioFiles"

def _text_to_audio(text):
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

def async_speak(text):
  """
  Crea un processo diverso per il TTS in modo che possa essere interrotto forzatamente 
  dal processo padre invocando la wake-word
  """
  filename = 'media/output.mp3'
  s = Sound(filename, speed=1.1)

  def _async_speak(s, text):
    filename = _text_to_audio(text)
    s.async_play()

  p = multiprocessing.Process(target=_async_speak, args=(s, text))
  p.start()
  return s