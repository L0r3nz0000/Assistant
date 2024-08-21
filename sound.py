import threading
from time import sleep
import subprocess
import os
from pydub import AudioSegment

class Sound:
  def __init__(self, filename, speed=1.0):
    if os.path.exists(filename):
      self.filename = filename
      self.speed = speed
      self.process = None
    else:
      print(f"File {filename} non trovato")
  
  def get_duration(self):
    # Carica il file audio
    audio = AudioSegment.from_file(self.filename)

    # Calcola la durata in secondi
    duration_s = len(audio) / 1000.0
    return duration_s

  def _delayed_play(self, delay):
    sleep(delay)
    self.async_play()

  def async_play(self, delay=0):
    if delay > 0:
      p = threading.Thread(target=self._delayed_play, args=(delay,))
      p.start()
    else:
      self.process = subprocess.Popen(["play", self.filename, "tempo", str(self.speed)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
  
  def play(self):
    subprocess.run(["play", self.filename, "tempo", str(self.speed)],
      stdout=subprocess.DEVNULL,
      stderr=subprocess.STDOUT)
  
  def stop(self):
    if self.process != None:
      self.process.terminate()
      return 0
    else:
      print("Processo già terminato")
      return 1