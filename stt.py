from redirect_output import suppress_stderr, restore_stderr
import speech_recognition as sr
from sound import Sound
from tts import speak

def listen_prompt(timeout=8):
  text = ""
  # Initialize the recognizer
  r = sr.Recognizer()

  s = Sound("sounds/active.mp3")
  s.delayed_play(delay=.3)

  old_stderr = suppress_stderr()

  with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source, duration=.3)

    print("Sono in ascolto... parla pure!")
    try:
      audio = r.listen(source, timeout=2, phrase_time_limit=timeout)

      try:
        print("Elaborando il messaggio...")
        text = r.recognize_google(audio, language="it-IT")
      except Exception as e:
        print("Exception:", e)
    except sr.exceptions.WaitTimeoutError:
      print("Exception: WaitTimeoutError")
      print("Scusa, non ho capito.")

  restore_stderr(old_stderr)  # Ripristina lo stderr
  return text
