import pvporcupine
import pyaudio
import struct
import os

access_key = "KLlwjiQgPwLdfVFeikjfBtM/+8GnlLdCvlQaLAtUwUVDDr4jPNEgdw=="

keyword_path = "wake_word_models/jarvis_it_linux_v3_0_0.ppn"
model_path = "wake_word_models/porcupine_params_it.pv"

def get_next_audio_frame(): pass

def listen_for_wake_word():
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
  
  print("Aspetto la parola di attivazione...")

  while True:
    pcm = audio_stream.read(handle.frame_length)
    pcm = struct.unpack_from("h" * handle.frame_length, pcm)
    keyword_index = handle.process(pcm)
    if keyword_index >= 0:
      handle.delete()
      return True