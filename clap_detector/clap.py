import pyaudio
import numpy as np
import time
from scipy.fftpack import fft

# Impostazioni per la registrazione
CHUNK = 1024  # Dimensione del blocco
FORMAT = pyaudio.paInt16  # Formato a 16 bit
CHANNELS = 1  # Mono
RATE = 44100  # Frequenza di campionamento (44.1kHz)
THRESHOLD = 200000  # Soglia di rilevamento per il battito di mani
MIN_FREQ = 14000  # Frequenza minima del battito di mani (Hz)
MAX_FREQ = 23000  # Frequenza massima del battito di mani (Hz)

# Funzione per analizzare le frequenze del segnale
# Funzione per analizzare le frequenze del segnale
def analyze_frequencies(audio_data):
  audio_data = np.frombuffer(audio_data, dtype=np.int16)
  fft_data = fft(audio_data)
  freqs = np.fft.fftfreq(len(fft_data), 1 / RATE)
  fft_data = np.abs(fft_data[:len(fft_data) // 2])
  freqs = freqs[:len(freqs) // 2]
  relevant_freqs = fft_data[(freqs >= MIN_FREQ) & (freqs <= MAX_FREQ)]
  return np.max(relevant_freqs) > THRESHOLD

# Funzione principale per ascoltare e rilevare battiti di mani
def clap_callback(callback, args=()):
  # Inizializza PyAudio
  p = pyaudio.PyAudio()
  
  # Apri lo stream audio
  stream = p.open(format=FORMAT,
                  channels=CHANNELS,
                  rate=RATE,
                  input=True,
                  frames_per_buffer=CHUNK)
  
  print("Ascolto per battiti di mani... (premi Ctrl+C per interrompere)")
  
  first_clap = False
  
  try:
    while True:
      # Analizza le frequenze del segnale audio
      clap = analyze_frequencies(stream.read(CHUNK))
      
      if clap:
        if not first_clap:
          first_clap = True
          start = time.time()
          print('first clap detected')
        else:
          first_clap = False
          if time.time() - start < .6:
            callback(*args)
      
      # Aspetta la fine del primo battito
      while clap:
        clap = analyze_frequencies(stream.read(CHUNK))
      
      time.sleep(0.01)  # Aggiungi un piccolo ritardo per evitare sovraccarico della CPU
  
  except KeyboardInterrupt:
    # Ferma lo stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Interrotto.")
        
# if __name__ == "__main__":
#   clap_callback(print, args=('double clap',))
