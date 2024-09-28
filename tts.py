from markdown import remove_markdown
import volume_controller
from sound import Sound
from time import time
import requests
import base64
import json
import os

# best voices: palmira, fiamma, lisandro, marcellomultilingual

def _text_to_audio(text, filename=None, voice="fiamma"):
  start = time()
  url = "https://audio.api.speechify.com/generateAudioFiles"
  text = remove_markdown(text)
  json = {
    "audioFormat": "mp3",
    "paragraphChunks": [
      text
    ],
    "voiceParams": {
      "engine": "azure",
      "languageCode": "it-IT",
      "name": voice
    }
  }

  r = requests.post(url, json=json)

  if "audioStream" not in r.json():
    return None
  
  audioStream_b64 = r.json()['audioStream']

  mp3_bytes = base64.b64decode(audioStream_b64)
  
  if not filename:
    filename = "sounds/output.mp3"

  with open(filename, "wb") as output_file:
    output_file.write(mp3_bytes)
  
  print(f"[{time() - start:.2f}s] Ottenuta la risposta vocale da azure.")
  return filename

def _play_voice(filename):
  if filename:
    with open("settings.json", "r") as file:
      settings = json.load(file)

    # Ottiene la lista delle app che stanno riproducendo audio
    #active_sinks = volume_controller.get_playing_audio_apps()

    # Abbassa il volume di tutte le app attive
    # for sink_id in active_sinks:
    #   volume_controller.set_volume(sink_id, settings['volume_decrease'])

    s = Sound(filename, speed=settings['output_speed'])
    s.play()

    # Riporta il volume delle app attive al valore iniziale
    # for sink_id in active_sinks:
    #   volume_controller.set_volume(sink_id, 100)

def speak(text, voice="fiamma"):
  text = text.strip()  # Elimina gli spazi inutili
  if text:
    if os.path.exists("sounds/output.mp3"):
      os.remove("sounds/output.mp3")
    filename = _text_to_audio(text, "sounds/output.mp3", voice)

    _play_voice(filename)