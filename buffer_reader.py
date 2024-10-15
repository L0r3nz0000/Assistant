from thread_exception import StoppableThread
from tts import _text_to_audio, _play_voice
import filter
from markdown import remove_markdown
from time import sleep
import os

class BufferReader:
  def __init__(self, chat, stream):
    self.audio_queue = []
    self.stream = stream
    self.chat = chat
    self.s = None
    self.stopped = False
    self.threads = []
    self.completed = False
    
  def read_from_stream(self, buffer_words=45, first_buffer=10):
    # Avvia il thread per riprodurre la coda audio
    self.threads.append(StoppableThread(target=self.play_queue))
    self.threads[-1].start()
    
    total_string = ""
    audio_index = 0
    
    for event in self.stream:
      if self.stopped:
        return
      if event.event_type == "text-generation":
        total_string += event.text
        
        total_string_no_tokens = remove_markdown(filter.remove_tokens(total_string))
        total_words = total_string_no_tokens.split()
        
        # Determina se è il momento di creare un buffer audio
        if (audio_index == 0 and len(total_words) > first_buffer) or \
          (audio_index > 0 and len(total_words) - first_buffer > buffer_words * audio_index):
          
          # Definisce l'intervallo di parole da includere nel buffer corrente
          start_word = 0 if audio_index == 0 else first_buffer + buffer_words * (audio_index - 1)
          # Numero di parole da leggere
          end_word = start_word + (first_buffer if audio_index == 0 else buffer_words)
          partial_buffer = " ".join(total_words[start_word:end_word])
          
          print(f"Buffer {audio_index + 1}: {len(partial_buffer.split())} parole")
          print(f"Contenuto: {partial_buffer}\n")
          
          # Crea un thread per generare l'audio
          self.threads.append(StoppableThread(target=self.add_buffer_to_queue, args=(partial_buffer, audio_index)))
          self.threads[-1].start()
          
          audio_index += 1
    
    # Controlla se ci sono parole rimanenti
    remaining_words = total_string_no_tokens.split()[first_buffer + buffer_words * (audio_index - 1):]
    if remaining_words:
      partial_buffer = " ".join(remaining_words)
      print(f"Buffer finale: {len(partial_buffer.split())} parole")
      print(f"Contenuto: {partial_buffer}\n")
      self.threads.append(StoppableThread(target=self.add_buffer_to_queue, args=(partial_buffer, audio_index)))
      self.threads[-1].start()

    # Salva l'output completo dopo la rimozione dei token
    total_string = remove_markdown(total_string)
    filter.execute_tokens(total_string)
    print("executing: " + total_string)
    self.chat.add_to_history_as_model(total_string)

  def add_buffer_to_queue(self, text, id):
    filename = f"sounds/output{id}.mp3"
    _text_to_audio(text, filename)
    self.audio_queue.append({'id': id, 'filename': filename})

  def play_queue(self):
    while not self.audio_queue: pass
    
    audio_number = 0
    
    while True:
      # Riproduce gli audio nell'ordine corretto
      for audio in self.audio_queue:
        if audio['id'] == audio_number:
          filename = audio['filename']
          print(f"Playing {filename}")
          # Riproduce l'audio
          self.s = _play_voice(filename, play_async=True)
          sleep(self.s.get_duration())
          # Rimuove l'audio dalla coda
          self.audio_queue.remove(audio)
          # Elimina il file audio
          os.remove(filename)
          audio_number += 1
          break  # Esce dal ciclo per riprodurre l'audio successivo
      
      if not self.audio_queue:  # Esce se la coda è vuota
        self.completed = True
        break
  
  def stop(self):
    if self.stream:
      self.stream.close()
    if self.s:
      self.s.stop()
      
    self.stopped = True
    
    for t in self.threads:
      t.terminate()
  
  
  
from coral import CoralChat

if __name__ == "__main__":
  # Reset history
  with open("history.json", "w") as file:
    file.write("[]")
    
  with open("system_prompt.txt", "r") as file:
    system = file.read()
    
  chat = CoralChat(system=system)
  
  generator = chat.send_message("cosa sai fare?")
  br = BufferReader(chat, generator)
  br.read_from_stream()