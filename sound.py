from pydub import AudioSegment
from time import sleep
import multiprocessing
import subprocess
import os

class Sound:
  def __init__(self, filename, speed=1.0):
    if filename:
      if os.path.exists(filename):
        self.filename = filename
        self.delay_process = None
        self.speed = speed
      else:
        print(f"File {filename} non trovato")
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
    self.play()

  def delayed_play(self, delay):
    self.delay_process = multiprocessing.Process(target=self._delayed_play, args=(delay,))
    self.delay_process.start()
    return self.delay_process.pid

  def async_play(self):
    self.delayed_play(0)
  
  def play(self):
    if self.filename:
      subprocess.run(["mpv", self.filename, f"--speed={self.speed}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)
  
  def stop(self):
    ok = False

    if self.delay_process != None:
      if self.delay_process.is_alive():
        self.delay_process.terminate()
        ok = True
    
    print("Processo già terminato" if not ok else "")
    return ok