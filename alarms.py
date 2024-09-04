from processes import kill_process_and_children
from time import time, sleep
from sound import Sound
from datetime import datetime
import multiprocessing
import signal
import json
import os

#TODO: testare queste funzioni

file_path = 'alarms.json'

def _search_alarm(alarms, time):
  for i, alarm in enumerate(alarms):
    if alarm["time"] == time:
      return i
  return -1

def _load_alarms(file_path):
  # Apri il file e carica il contenuto
  if os.path.exists(file_path):
    with open(file_path, 'r') as file:
      return json.load(file)
  else:
    return []

def _get_alarm_pid(time):
  alarms = _load_alarms(file_path)
  
  alarm = _search_alarm(alarms, time)
  return alarm['pid'] if alarm != -1 else -1

# Salva le modifiche applicate al json dei timer
def _save(alarms):
  with open(file_path, 'w') as file:
    json.dump(alarms, file, indent=2)

def _start_alarm(time):
  s = Sound("sounds/alarm.mp3")
  now = datetime.now()

  while now.strftime("%H:%M") != time:
    sleep(1)

  # Riproduce il suono allo scadere del tempo
  s.play()

  alarm = _search_alarm(_load_alarms(file_path), time)
  
  if alarm != -1:
    # Il timer non deve ripetersi
    if not alarm['repeats']:
      # Elimina il timer dalla lista
      _remove_alarm(_load_alarms(file_path), time)
  
# Avvia un timer asincrono e ritorna il pid
def start_alarm(time, repeats):
  # Verifica che l'id del timer sia unico
  if _search_alarm(_load_alarms(file_path), time) != -1:
    return False
  
  # Crea il processo per il timer
  alarm_process = multiprocessing.Process(target=_start_alarm, args=(time))
  alarm_process.daemon = False
  alarm_process.start()  # Avvia il processo

  pid = alarm_process.pid

  print(f"Nuovo timer impostato id:{id} pid:{pid}")

  save_alarm({
    "time": time,
    "pid": pid,
    "repeats": repeats
  })
  
  return True

def _remove_alarm(alarms, time):
  for i, timer in enumerate(alarms):
    if timer["time"] == time:
      alarms.pop(i)
      _save(alarms)
      return True
  return False

def stop_alarm(time):
  alarms = _load_alarms(file_path)

  # Cerca l'id del timer e lo interrompe inviando un SIGTERM al processo
  for alarm in alarms:
    if alarm["time"] == time:
      _remove_alarm(alarms, time)
      pid = alarm["pid"]
      
      try:
        kill_process_and_children(pid)
      except ProcessLookupError:
        print("la sveglia non è stata trovata, forse era già scaduto?")
      
      return True
  return False

def get_remaining(id):
  timers = _load_alarms(file_path)

  for timer in timers:
    if timer['id'] == id:
      return timer['seconds'] - timer['elapsed']
  return -1


def save_alarm(alarm):
  alarms = _load_alarms(file_path)
  time = alarm['time']
  
  i = _search_alarm(alarms, time)
  if i != -1:
    print("Impossibile creare due sveglie alla stessa ora")
    return
  alarms.append(alarm)
  
  _save(alarms)