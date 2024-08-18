import speech_recognition as sr
from sounds import async_sound
from tts import speak

def listen_prompt(timeout=8):
  text = ""
  # Initialize the recognizer
  r = sr.Recognizer()
  async_sound("media/active.mp3", delay=.3)
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
      print("Scusa, non ho capito.")
  return text
