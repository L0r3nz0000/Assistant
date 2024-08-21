import multiprocessing
import pvporcupine
import threading
import pyaudio
import struct
import time
import sys
import os

access_key = "KLlwjiQgPwLdfVFeikjfBtM/+8GnlLdCvlQaLAtUwUVDDr4jPNEgdw=="

keyword_path = "wake_word_models/jarvis_it_linux_v3_0_0.ppn"
model_path = "wake_word_models/porcupine_params_it.pv"

def get_next_audio_frame(): pass

# Aspetta la parola di attivazione
def blocking_wake_word():
  print('\x1b[34m\x1b[1m')
  handle = pvporcupine.create(
    access_key=access_key,
    keyword_paths=[keyword_path],
    model_path=model_path
  )

  pa = pyaudio.PyAudio()

  audio_stream = pa.open(
    rate=handle.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=handle.frame_length)
  
  os.system("clear")
  print('\x1b[0m')
  
  print("Aspetto la parola di attivazione...")

  try:
    while True:
      pcm = audio_stream.read(handle.frame_length)
      pcm = struct.unpack_from("h" * handle.frame_length, pcm)
      keyword_index = handle.process(pcm)
      if keyword_index >= 0:
        print("Attivo")
        return True
  finally:
    audio_stream.close()  # Chiude lo stream audio
    pa.terminate()        # Termina PyAudio
    handle.delete()       # Elimina l'handle di Porcupine

def async_wake_word_callback(callback, args=()):
  p = None
  while True:
    blocking_wake_word()
    if p == None:
      p = callback(*args)
    else:
      p = callback(p)
    #time.sleep(20)

"""def async_wake_word_callback(callback, args=()):
  def _wake_word_callback(callback, args):
    blocking_wake_word()  # Aspetta la parola di attivazione
    callback(* args)

  t = threading.Thread(target=_wake_word_callback, args=(callback, args))
  t.start()"""