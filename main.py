from wake_word import blocking_wake_word
from updates import fetch_updates
from ChatState import ChatState
#from stt import listen_prompt
<<<<<<< HEAD
from vosk_real_time import recognize_word
from devices.devices import power_off, power_on
=======
from vosk_microfone.vosk_real_time import recognize_word
from devices import power_off, power_on
>>>>>>> instant_wake_word
#import multiprocessing
from thread_exception import StoppableThread
#from clap_detector.clap import MyTapTester
from time import time
from tts import speak
import subprocess
import threading
import json
import os

# chat inizializzata a None per non perdere il riferimanto (per il garbage collector)
chat = None
activation_word = "alexa"

def new_interaction(user_prompt, conversation_open, response_completed, update_available):
  chat = ChatState(system=system_prompt)
  
  with open('settings.json', 'r') as file:
    settings = json.load(file)
  
  if update_available.is_set() and settings['ask_for_updates']:
    update_available.clear()
    question = "Ciao, è disponibile un aggiornamento, vuoi farlo ora?"
    speak(question)
    
    chat.add_to_history_as_model(question)

  thread = StoppableThread(target=interaction, args=(chat, user_prompt, conversation_open, response_completed))
  thread.start()
  return thread

def interaction(chat, user_prompt, conversation_open, response_completed):
  response_completed.clear()

  if user_prompt:
    print('\033[94m' + 'User:' + '\033[39m', user_prompt)
    start = time()
    output = chat.send_message(user_prompt).strip()
    print(f"[{time() - start:.2f}s] Ottenuta risposta testuale da llama.")
    print('\033[94m' + 'Model:' + '\033[39m', output)

    if output:
      if '$END' in output:
        # La conversazione è chiusa
        conversation_open.clear()
        output = output.replace('$END', '')
      else:
        # La conversazione continua
        conversation_open.set()
      
      speak(output)
  else:
    print(f"input non valido: '{user_prompt}'")
    conversation_open.clear()
  response_completed.set()

if __name__ == "__main__":
  conversation_open = threading.Event()  # Default False
  response_completed = threading.Event()
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
    
  # Loop eventi
  user_prompt = recognize_word(activation_word)
  t = new_interaction(user_prompt, conversation_open, response_completed, update_available)

  while True:
    user_prompt = recognize_word(activation_word)
    t.terminate()
    print("Thread interrotto")

    print("Sto creando un nuovo thread...")
    t = new_interaction(user_prompt, conversation_open, response_completed, update_available)