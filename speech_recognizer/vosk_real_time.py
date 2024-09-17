import json
import pyaudio

from vosk import Model, KaldiRecognizer, SetLogLevel
import os

model_name = "vosk-model-it-0.22/"
model_path = os.path.join(os.path.dirname(__file__), model_name)

# Load the Vosk model
model = Model(model_path)

SAMPLE_RATE = 16000
FRAME_LENGTH = 4096
MINIMUM_CONFIDENCE_VOSK = 0.6

def recognize_word(activation_word):
  # Inizializza pyaudio
  pa = pyaudio.PyAudio()

  # Apre uno stream dal microfono
  audio_stream = pa.open(
    rate=SAMPLE_RATE,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=FRAME_LENGTH)
  
  SetLogLevel(-1)
  
  print(f"Aspetto la parola {activation_word}...")
  
  # Inizializza il recognizer con il modello
  rec = KaldiRecognizer(model, SAMPLE_RATE)
  rec.SetWords(True)
  rec.SetPartialWords(True)

  try:
    while True:
      # Legge un frame audio dal microfono
      data = audio_stream.read(FRAME_LENGTH)
      if len(data) == 0:
        return None
      
      # Passa il frame audio al modello
      if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        
        prompt = ""
        if 'result' in result:
          # Ricostruisce la frase a partire dalle parole che superano la "minimum confidence"
          for word in result['result']:
            if word['conf'] >= MINIMUM_CONFIDENCE_VOSK:
              prompt += word['word'] + ' '
          prompt = prompt.strip()
        
        # Verifica che sia stata riconosciuta almeno una parola
        if prompt:
          # Se viene riconosciuta la parola di attivazione, restituisce la frase
          if activation_word in prompt:
            return prompt.strip()

  finally:
    audio_stream.close()        # Chiude lo stream audio
    pa.terminate()              # Termina PyAudio

if __name__ == "__main__":
  print(recognize_word('alexa'))