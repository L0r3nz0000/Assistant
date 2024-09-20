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

  def read_from_stream(self, buffer_words=45, first_buffer=6):
    # Esegue il thread per riprodurre i file audio
    threading.Thread(target=self.play_queue, args=()).start()
    
    total_string = ""
    audio_index = 0
    
    for event in self.generator:
      total_string += str(event)
      total_string_no_tokens = filter.remove_tokens(total_string)
      
      total_words = len(total_string_no_tokens.split())
      
      # Determina se è il primo buffer o uno successivo
      if (audio_index == 0 and total_words > first_buffer) or (audio_index > 0 and total_words >= (buffer_words * (audio_index + 1))):
        if audio_index == 0:  # Primo buffer
          partial_buffer = " ".join(total_string_no_tokens.split()[:first_buffer])
          print(f"Primo buffer: {len(partial_buffer.split())} parole")
        else:  # Buffer successivi
          start_word = first_buffer + buffer_words * (audio_index - 1)
          end_word = start_word + buffer_words
          partial_buffer = " ".join(total_string_no_tokens.split()[start_word:end_word])
          print(f"Buffer numero {audio_index + 1}, {len(partial_buffer.split())} parole")
        
        # Stampa il contenuto del buffer
        print(f"Contenuto: {partial_buffer}\n")
        
        # Crea un thread per generare l'audio
        threading.Thread(target=self.add_buffer_to_queue, args=(partial_buffer, audio_index, f"sounds/output{audio_index}.mp3")).start()
        
        audio_index += 1
    
    # Verifica se ci sono parole rimaste da elaborare
    total_string_no_tokens = filter.remove_tokens(total_string)
    remaining_words = total_string_no_tokens.split()[first_buffer + buffer_words * audio_index:]
    
    if remaining_words:
      partial_buffer = " ".join(remaining_words)
      threading.Thread(target=self.add_buffer_to_queue, args=(partial_buffer, audio_index, f"sounds/output{audio_index}.mp3")).start()

    # Ripristina i token e salva l'output completo
    filter.replace_tokens(total_string)
    print("Output completo:", total_string)
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


from ChatState import ChatState

if __name__ == "__main__":
  with open("system_prompt.txt", "r") as file:
    system = file.read()
    
  chat = ChatState(system=system)
  
  generator = chat.send_message("cosa sai fare?")
  br = BufferReader(chat, generator)
  br.read_from_stream()