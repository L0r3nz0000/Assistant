from redirect_output import suppress_stderr, restore_stderr
import speech_recognition as sr
import volume_controller
from sound import Sound
import json

def listen_prompt(timeout=8):
  # Ottiene la lista delle app che stanno riproducendo audio
  active_sinks = volume_controller.get_playing_audio_apps()

  with open("settings.json", "r") as file:
    settings = json.load(file)

  # Abbassa il volume di tutte le app attive
  for sink_id in active_sinks:
    volume_controller.set_volume(sink_id, settings['volume_decrease'])

  text = ""
  # Inizializza il Recognizer
  r = sr.Recognizer()

  # Riproduce il suono di attivazione
  s = Sound("sounds/active.mp3")
  s.delayed_play(delay=.3)

  # Ridireziona lo stderr a /dev/null
  old_stderr = suppress_stderr()

  with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source, duration=.2)

    print("Sono in ascolto... parla pure!")
    try:
      audio = r.listen(source, timeout=3, phrase_time_limit=timeout)

      # Riporta il volume delle app attive al valore iniziale
      for sink_id in active_sinks:
        volume_controller.set_volume(sink_id, 100)

      try:
        print("Elaborando il messaggio...")
        text = r.recognize_google(audio, language="it-IT")
      except Exception as e:
        print("Exception:", e)
    except sr.exceptions.WaitTimeoutError:
      print("Exception: WaitTimeoutError")
      print("Scusa, non ho capito.")

  # Ripristina lo stderr
  restore_stderr(old_stderr)
  return text
