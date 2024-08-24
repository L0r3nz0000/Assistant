from processes import kill_process_and_children
from time import time, sleep
from sound import Sound
import multiprocessing
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

def _start_timer(id, seconds):
  s = Sound("sounds/timer.mp3")
  
  start = time()
  elapsed = 0

  while time() - start < seconds:
    sleep(1)
    elapsed += 1

    # Carica i timer dal file
    timers = _load_timers(file_path)

    for i, timer in enumerate(timers):
      if timer['id'] == id:
        timers[i]['elapsed'] = elapsed
    
    _save(timers)

  # Riproduce il suono allo scadere del tempo
  s.play()

  # Elimina il timer dalla lista
  _remove_timer(id)
  
# Avvia un timer asincrono e ritorna il pid
def start_timer(id, seconds):
  # Verifica che l'id del timer sia unico
  if _search_timer(_load_timers(file_path), id) != -1:
    return False
  
  # Crea il processo per il timer
  timer_process = multiprocessing.Process(target=_start_timer, args=(id, seconds))
  timer_process.daemon = False
  timer_process.start()  # Avvia il processo

  pid = timer_process.pid

  print(f"Nuovo timer impostato id:{id} pid:{pid}")

  save_timer({
    "id": id,
    "pid": pid,
    "seconds": seconds,
    "elapsed": 0
  })
  
  return True

def _remove_timer(id):
  timers = _load_timers(file_path)
  for i, timer in enumerate(timers):
    if timer["id"] == id:
      timers.pop(i)
      _save(timers)
      return True
  return False

def stop_timer(id):
  timers = _load_timers(file_path)

  # Cerca l'id del timer e lo interrompe inviando un SIGTERM al processo
  for i, timer in enumerate(timers):
    if timer["id"] == id:
      pid = timer["pid"]
      _remove_timer(id)

      try:
        os.kill(pid, signal.SIGTERM)
        #kill_process_and_children(pid)
      except ProcessLookupError:
        print("Il timer non è stato trovato, forse era già scaduto?")
      
      _save(timers)
      return True
  return False

def get_remaining(id):
  timers = _load_timers(file_path)

  for timer in timers:
    if timer['id'] == id:
      return timer['seconds'] - timer['elapsed']
  return -1

def save_timer(timer):
  timers = _load_timers(file_path)
  
  i = _search_timer(timers, id)
  if i != -1:
    print("Impossibile creare due timer con lo stesso id")
    return
  timers.append(timer)
  
  _save(timers)