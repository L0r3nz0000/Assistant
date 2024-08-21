import speech_recognition as sr
from sound import Sound
from tts import speak

def listen_prompt(timeout=8):
  text = ""
  # Initialize the recognizer
  r = sr.Recognizer()

  s = Sound("media/active.mp3")
  s.async_play(delay=.3)

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
  return text
