from processes import kill_process_and_children
import pvporcupine
import pyaudio
import struct
import sys
import os

access_key = "KLlwjiQgPwLdfVFeikjfBtM/+8GnlLdCvlQaLAtUwUVDDr4jPNEgdw=="

keyword_path = "wake_word_models/jarvis_it_linux_v3_0_0.ppn"
model_path = "wake_word_models/porcupine_params_it.pv"

def get_next_audio_frame(): pass

# Aspetta la parola di attivazione
def blocking_wake_word(conversation_open, response_completed):
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
  
  print('\x1b[0m')
  
  print("Aspetto la parola di attivazione...")

  try:
    while True:
      if response_completed.is_set() and conversation_open.is_set():
        return False
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

def wake_word_callback(new_interaction, conversation_open, response_completed, args=()):
  # Passando conversation_open come stop_flag, se l'assistente vorrà aprire una nuova
  # interazione verrà interrotta l'attesa della wake word e aperto un nuovo processo
  blocking_wake_word(conversation_open, response_completed)
  p = new_interaction(*args)

  while True:
    blocking_wake_word(conversation_open, response_completed)
    if p.is_alive():
      kill_process_and_children(p.pid)
      print("Processo interrotto")

    print("Sto creando un nuovo processo...")
    p = new_interaction(*args)