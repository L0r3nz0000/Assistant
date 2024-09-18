import threading
from tts import _text_to_audio, _play_voice
from ChatState import ChatState
import os

class BufferReader:
  def __init__(self, generator):
    self.audio_queue = []
    self.generator = generator
    
  def read_from_stream(self, buffer_words=8):
    text_buffer = ""
    i = 1
    audio_number = 0
    
    # Esegue il thread per riprodurre i batch audio
    threading.Thread(target=self.play_queue, args=()).start()
    
    for event in self.generator:
      text_buffer += str(event)
      
      # Numero di parole già generate
      generated_words = len(text_buffer.split())
      if generated_words >= buffer_words:
        # Crea un thread per generare l'audio in batch
        threading.Thread(target=self.add_buffer_to_queue, args=(text_buffer, audio_number, f"sounds/output{audio_number}.mp3")).start()
        audio_number += 1
        
        text_buffer = ""
        i = 0
      i += 1
    
    # Se mancano ancora dei token genera l'ultimo buffer
    if i > 1:
      threading.Thread(target=self.add_buffer_to_queue, args=(text_buffer, audio_number, f"sounds/output{audio_number}.mp3")).start()

  def add_buffer_to_queue(self, text, id, filename):
    _text_to_audio(text, filename)
    self.audio_queue.append({'id': id, 'filename': filename})

  def play_queue(self):
    # Aspetta che sia disponibile il primo file audio
    while len(self.audio_queue) == 0: pass
    
    audio_number = 0
    # Mentre ci sono degli audio da riprodurre
    # Li riproduce i ordine
    while len(self.audio_queue):
      print(f"cerco audio {audio_number}")
      for i, audio in enumerate(self.audio_queue):
        # Cerca l'audio corrispondente
        if audio['id'] == audio_number:
          filename = audio['filename']
          
          print(f"playing {filename}")
          _play_voice(filename)
          # Rimuove dalla lista dei file quello appena riprodotto
          self.audio_queue.pop(i)
          # Elimina il file
          os.remove(filename)
          audio_number += 1

import time

if __name__ == "__main__":
  with open('system_prompt.txt', 'r') as file:
    system_prompt = file.read()
    
  chat = ChatState(system=system_prompt)
  
  start = time.time()
  generator = chat.send_message("ciao, cosa sai fare?")
  print(f"[{time.time() - start:.2f}] Generato primo token")
  br = BufferReader(generator)
  br.read_from_stream()