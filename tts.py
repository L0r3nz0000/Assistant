import requests
import base64
from sounds import play_sound
import os

s = requests.Session()

json = {
	"audioFormat": "mp3",
	"paragraphChunks": [
		""
	],
	"voiceParams": {
		"engine": "azure",
		"languageCode": "it-IT",
		"name": "palmira"
	}
}

endpoint = "https://audio.api.speechify.com/generateAudioFiles"

def speak(text):
  json['paragraphChunks'][0] = text
  r = s.post(endpoint, json=json)

  if "audioStream" not in r.json():
    return
  
  audioStream_b64 = r.json()['audioStream']

  mp3_bytes = base64.b64decode(audioStream_b64)
  output_file_name = "media/output.mp3"

  with open(output_file_name, "wb") as output_file:
    output_file.write(mp3_bytes)

  play_sound(output_file_name, speed=1.1)