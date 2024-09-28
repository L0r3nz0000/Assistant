from pydub import AudioSegment
from time import sleep
from thread_exception import StoppableThread
#! trovare una libreria per l'audio


import pygame

import os

class Sound:
  def __init__(self, filename, speed=1.0):
    if filename:
      if os.path.exists(filename):
        self.filename = filename
        self.delay_thread = None
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
    self.delay_thread = StoppableThread(target=self._delayed_play, args=(delay,))
    self.delay_thread.start()
    
  def _play(self):
    if self.filename:
      # Imposta la frequenza
      pygame.mixer.init(frequency=int(44100 * self.speed))

      # Carica l'audio
      pygame.mixer.music.load(self.filename)
      pygame.mixer.music.play()
    else:
      print("File non trovato")
      
  def async_play(self):
    self._play()
  
  def play(self):
    self._play()
    try:
      sleep(self.get_duration())
    except KeyboardInterrupt:
      self.stop()
      
  def stop(self):
    pygame.mixer.quit()