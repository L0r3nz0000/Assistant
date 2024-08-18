import threading
import subprocess

def play_sound(filename, speed=1.0):
  subprocess.run(["play", filename, "tempo", str(speed)], 
    stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

def async_sound(filename, speed=1.0, delay=0):
  def play_sound():
    retcode = subprocess.call(["play", filename, "tempo", str(speed)], 
      stdout=subprocess.DEVNULL,
      stderr=subprocess.STDOUT)

  # Usa threading.Timer per avviare il thread dopo il delay specificato
  player_timer = threading.Timer(delay, play_sound)
  player_timer.start()