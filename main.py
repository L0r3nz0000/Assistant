from wake_word import blocking_wake_word
from updates import fetch_updates, ask_for_updates
from ChatState import ChatState
from stt import listen_prompt
import multiprocessing
from tts import speak
import threading
import signal
import os

def new_interaction(conversation_open, response_completed, update_available):
  chat = ChatState(system=system_prompt)
  user_prompt = ""
  if not update_available.is_set():
    user_prompt = listen_prompt()
  else:
    # Se ci sono aggiornamenti disponibili chiede all'utente se vuole farli
    if update_available.is_set():
      update_available.clear()
      user_prompt = ask_for_updates(chat)

  process = multiprocessing.Process(target=interaction, args=(chat, user_prompt, conversation_open, response_completed, update_available))
  process.start()
  return process

def interaction(chat, user_prompt, conversation_open, response_completed, update_available):
  response_completed.clear()

  if user_prompt:
    print('\033[94m' + 'User:' + '\033[39m', user_prompt)

    output = chat.send_message(user_prompt).strip()
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
    speak("Scusa, non ho capito.")
    conversation_open.clear()
  response_completed.set()

if __name__ == "__main__":
  conversation_open = multiprocessing.Event()  # Default False
  response_completed = multiprocessing.Event()
  update_available = multiprocessing.Event()
  
  updates_thread = threading.Thread(target=fetch_updates, args=(update_available,))
  updates_thread.start()

  with open("system_prompt.txt", "r") as file:
    system_prompt = file.read()
  
  import time;time.sleep(3 )
  print("Aggiornamenti disponibili" if update_available.is_set() else "Aggiornamenti non disponibili")
  
  blocking_wake_word(conversation_open, response_completed, update_available)
  p = new_interaction(conversation_open, response_completed, update_available)

  while True:
    blocking_wake_word(conversation_open, response_completed, update_available)
    if p.is_alive():
      os.kill(p.pid, signal.SIGTERM)
      print("Processo interrotto")

    print("Sto creando un nuovo processo...")
    p = new_interaction(conversation_open, response_completed, update_available)