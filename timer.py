from sound import Sound
import signal
import json
import os

file_path = 'timers.json'

def _search_timer(timers, id):
  for i, timer in enumerate(timers):
    if timer["id"] == id:
      return i
  return -1

def _load_timers(file_path):
  # Apri il file e carica il contenuto
  if os.path.exists(file_path):
    with open(file_path, 'r') as file:
      return json.load(file)
  else:
    return []

def _get_timer_pid(id):
  timers = _load_timers(file_path)
  for timer in timers:
    if timer["id"] == id:
      return timer["pid"]
  return -1

# Salva le modifiche applicate al json dei timer
def _save(timers):
  with open(file_path, 'w') as file:
    json.dump(timers, file, indent=2)
  
# Avvia un timer asincrono e ritorna il pid
def start_timer(id, seconds):
  if _search_timer(_load_timers(file_path), id) != -1:
    print(f"Impossibile creare due timer con lo stesso id: {id}")
    return -1
  s = Sound("sounds/timer.mp3")
  pid = s.delayed_play(delay=seconds)
  return pid
  
def stop_timer(id):
  timers = _load_timers(file_path)

  # Cerca l'id del timer e lo interrompe inviando un SIGTERM al processo
  for i, timer in enumerate(timers):
    if timer["id"] == id:
      pid = timer["pid"]
      timers.pop(i)
      try:
        os.kill(pid, signal.SIGTERM)
      except ProcessLookupError:
        print("Il timer non è stato trovato, forse era già scaduto?")
      
      _save(timers)
      return True
  return False

def save_timer(timer):
  timers = _load_timers(file_path)
  
  i = _search_timer(timers, id)
  if i != -1:
    print("Impossibile creare due timer con lo stesso id")
    return
  timers.append(timer)
  
  _save(timers)