import replicate
import requests
from time import time

def upload_audio_file(path):
  start = time()
  with open(path, 'rb') as file:
    files = {'file': file}
    response = requests.post('http://0x0.st', files=files)
  print("tempo upload:", time() - start)
  return response.text.strip()

def whisper(url):
  start = time()
  output = replicate.run(
    "vaibhavs10/incredibly-fast-whisper:3ab86df6c8f54c11309d4d1f930ac292bad43ace52d10c80d87eb258b3c9f79c",
    input={
      "task": "transcribe",
      "audio": url,
      "language": "italian", # "language": "None" per riconoscere la lingua in automatico
      "timestamp": "chunk",
      "batch_size": 64,
      "diarise_audio": False
    }
  )
  print("tempo whisper:", time() - start)
  return output['text']


if __name__ == "__main__":
  print("file prova.wav:")
  url = upload_audio_file("prova.wav")
  output = whisper(url)
  print(output + "\n")
  
  print("file prova.mp3:")
  url = upload_audio_file("prova.mp3")
  output = whisper(url)
  print(output)