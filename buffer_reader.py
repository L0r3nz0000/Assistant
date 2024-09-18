import threading
from tts import _text_to_audio, _play_voice
from ChatState import ChatState
import os

class BufferReader:
  def __init__(self, generator):
    self.audio_queue = []
    self.generator = generator
    
  def read_from_stream(self, buffer_tokens=10):
    text_buffer = ""
    i = 1
    audio_number = 0
    
    # Esegue il thread per riprodurre i batch audio
    threading.Thread(target=self.play_queue, args=()).start()
    
    for event in self.generator:
      text_buffer += str(event)
      
      if i >= buffer_tokens:
        # Crea un thread per generare l'audio in batch
        threading.Thread(target=self.add_buffer_to_queue, args=(text_buffer, f"sounds/output{audio_number}.mp3")).start()
        audio_number += 1
        
        text_buffer = ""
        i = 0
      i += 1
    
    # Se mancano ancora dei token genera l'ultimo buffer
    if i > 1:
      threading.Thread(target=self.add_buffer_to_queue, args=(text_buffer, f"sounds/output{audio_number}.mp3")).start()

  def add_buffer_to_queue(self, text, filename):
    _text_to_audio(text, filename)
    self.audio_queue.append(filename)

  def play_queue(self):
    while len(self.audio_queue) == 0: pass
    
    for filename in self.audio_queue:
      _play_voice(filename)
      os.remove(filename)

import replicate

if __name__ == "__main__":
  with open('system_prompt.txt', 'r') as file:
    system_prompt = file.read()
    
  chat = ChatState(system=system_prompt)
  
  generator = chat.send_message("ciao, cosa sai fare?")
  br = BufferReader(generator)
  br.read_from_stream()