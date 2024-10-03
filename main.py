from updates import fetch_updates
from speech_recognizer.vosk_real_time import recognize_word
from buffer_reader import BufferReader
from coral import CoralChat
import subprocess
import threading
import json
import os

activation_word = "coral"

def interaction(chat, user_prompt, conversation_open):
  if user_prompt:
    print('\033[94m' + 'User:' + '\033[39m', user_prompt)
    
    # Invia il messaggio a replicate e ritorna il generatore
    generator = chat.send_message(user_prompt)
    
    br = BufferReader(chat, generator)
    # Genera e riproduce dei buffer audio a partire dallo stream replicate
    br.read_from_stream()
  else:
    print(f"input non valido: '{user_prompt}'")
    conversation_open.clear()

if __name__ == "__main__":
  conversation_open = threading.Event()  # Default False
  update_available = threading.Event()
  
  if not os.path.exists('settings.json'):
    default_settings = {
      "output_speed": 1.1,
      "ask_for_updates": True,
      "volume_decrease": 30,
      "min_tokens": -1,
      "max_tokens": 1024,
      "temperature": 0.5,
      "length_penalty": 0.5
    }
    with open('settings.json', 'w') as file:
      json.dump(default_settings, file, indent=2)
  
  with open('settings.json', 'r') as file:
    default_settings = json.load(file)
  
  if default_settings['ask_for_updates']:
    updates_thread = threading.Thread(target=fetch_updates, args=(update_available,))
    updates_thread.start()
  
  # Esegue il server flask per spotify connect
  subprocess.Popen([".env/bin/python3", "-m", "flask", "run"], cwd='spotify-free-api')

  # Carica il prompt system dal file
  with open("system_prompt.txt", "r") as file:
    system_prompt = file.read()
  
  chat = CoralChat(system=system_prompt)
  
  # Loop eventi
  while True:
    user_prompt = recognize_word(activation_word)
    interaction(chat, user_prompt, conversation_open)