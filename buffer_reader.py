import threading
from tts import _text_to_audio, _play_voice
import filter
import os
import re

class BufferReader:
  def __init__(self, chat, generator):
    self.audio_queue = []
    self.generator = generator
    self.chat = chat
    
  def read_from_stream(self, buffer_words=10):
    text_buffer = ""
    i = 1
    audio_number = 0
    
    # Esegue il thread per riprodurre i batch audio
    threading.Thread(target=self.play_queue, args=()).start()
    total_string = ""
    
    for event in self.generator:
      text_buffer += str(event)
      total_string += str(event)
      
      # Numero di parole già generate
      generated_words = len(text_buffer.split())
      if generated_words > buffer_words:
        # Rimuove l'ultima parola
        partial_buffer = " ".join(text_buffer.split()[:-1]) if len(text_buffer.split()) > 1 else text_buffer
        
        # *Rimuove i token riconosciuti per non leggerli ad alta voce
        for regex in filter.filters:
          partial_buffer = re.sub(filter.filters[regex], '', partial_buffer) 
        for f in filter.functions:
          partial_buffer = partial_buffer.replace(f, '')
        
        # Crea un thread per generare l'audio in batch
        threading.Thread(target=self.add_buffer_to_queue, args=(partial_buffer, audio_number, f"sounds/output{audio_number}.mp3")).start()
        audio_number += 1
        
        text_buffer = text_buffer.split()[-1] + ' '
        i = 0
      i += 1
      
    # *Rimuove i token riconosciuti per non leggerli ad alta voce
    for regex in filter.filters:
      text_buffer = re.sub(filter.filters[regex], '', text_buffer) 
    for f in filter.functions:
      text_buffer = text_buffer.replace(f, '')
          
    # Se mancano ancora dei token genera l'ultimo buffer
    if i > 1:
      threading.Thread(target=self.add_buffer_to_queue, args=(text_buffer, audio_number, f"sounds/output{audio_number}.mp3")).start()

    filter.replace_tokens(total_string)
    self.chat.add_to_history_as_model(total_string)

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
