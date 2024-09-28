from timer.timer import start_timer, stop_timer, _get_timer_pid, get_remaining
from readable_time import convert_seconds_to_readable_time
from volume_controller import set_master_volume
from alarm.alarm import start_alarm, stop_alarm
from event import new_event
from tts import speak
from devices.devices import power_on, power_off
import webbrowser
import subprocess
import threading
import requests
import json
import os
import re

# Filtri regex
filters = {
  'pattern_alarm' : r'\$SET_ALARM\s+(\d{1,2}:\d{1,2})\s+(true|false)',                     #   $SET_ALARM hh:mm repeats
  'pattern_turn_on' : r'\$TURN_ON_DEVICE\s+(\d+)',                                         #   $TURN_ON device_id
  'pattern_turn_off' : r'\$TURN_OFF_DEVICE\s+(\d+)',                                       #   $TURN_OFF device_id
  'pattern_add_song_to_queue' : r'\$ADD_SONG_TO_QUEUE\s+"(\S+)"',                          #   $ADD_SONG_TO_QUEUE name
  'pattern_add_artist_to_queue' : r'\$ADD_ARTIST_TO_QUEUE\s+"(\S+)"',                      #   $ADD_ARTIST_TO_QUEUE name
  'pattern_add_album_to_queue' : r'\$ADD_ALBUM_TO_QUEUE\s+"(\S+)"',                        #   $ADD_ALBUM_TO_QUEUE name
  'pattern_add_playlist_to_queue' : r'\$ADD_PLAYLIST_TO_QUEUE\s+"(\S+)"',                  #   $ADD_PLAYLIST_TO_QUEUE name
  'pattern_play_artist' : r'\$PLAY_ARTIST\s+"(\S+)"',                                      #   $PLAY_ARTIST name
  'pattern_play_playlist' : r'\$PLAY_PLAYLIST\s+"(\S+)"',                                  #   $PLAY_PLAYLIST name
  'pattern_play_album' : r'\$PLAY_ALBUM\s+"(\S+)"',                                        #   $PLAY_ALBUM name
  'pattern_play_song' : r'\$PLAY_SONG\s+"(\S+)"',                                          #   $PLAY_SONG name
  'pattern_volume' : r'\$SET_MASTER_VOLUME\s+(\d+)',                                       #   $SET_MASTER_VOLUME percentage
  'pattern_timer' : r'\$SET_TIMER\s+(\d+)\s+(\d+)',                                        #   $SET_TIMER id seconds
  'pattern_stop_timer' : r'\$STOP_TIMER\s+(\d+)',                                          #   $STOP_TIMER id
  'pattern_remaining' : r'\$GET_TIMER_REMAINING\s+(\d+)',                                  #   $GET_TIMER_REMAINING id
  'pattern_speed' : r'\$SET_SPEED\s+(\d+(\.\d+)?)',                                        #   $SET_SPEED speed
  'pattern_url' : r'\$OPEN_URL\s+"(\S+)"',                                                 #   $OPEN_URL "url"
  'pattern_python' : r'```python(.*?)```',                                                 #   ```python    code    ```
  'pattern_bash' : r'```bash(.*?)```',                                                     #   ```bash      code    ```
  'pattern_event' : r'\$NEW_EVENT\s+(\S+)\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{1,2})',  #   $NEW_EVENT titolo dd/mm/yyyy hh:mm
}

python_interpreter = "python3"
bash_interpreter = "bash"

def execute(command):
  threading.Thread(target=subprocess.run, args=(command.split(),)).start()

def execute_and_remove_python_tags(text, remove=False):
  # Estrai tutto il contenuto tra i tag python
  matches = re.findall(filters['pattern_python'], text, re.DOTALL)
  
  # Rimuovi i tag python dalla stringa originale
  modified_text = re.sub(filters['pattern_python'], '', text, flags=re.DOTALL)

  for match in matches:
    i = 0
    while os.path.exists(f'scripts/script-{i+1}.py'):
      i += 1

    with open(f'scripts/script-{i+1}.py', 'w') as file:
      file.write(match)
    print("\033[91m" + "Eseguendo lo script python..." + "\033[39m")
    execute(f'{python_interpreter} scripts/script-{i+1}.py')
  
  return modified_text if remove else text

def execute_and_remove_code_blocks(text, remove=False):
  # Estrai tutto il contenuto tra i delimitatori bash
  matches = re.findall(filters['pattern_bash'], text, re.DOTALL)
  
  # Rimuovi i blocchi di codice bash dalla stringa originale
  modified_text = re.sub(filters['pattern_bash'], '', text, flags=re.DOTALL)

  for match in matches:
    i = 0
    while os.path.exists(f'scripts/script-{i+1}.sh'):
      i += 1

    with open(f'scripts/script-{i+1}.sh', 'w') as file:
      file.write(match)
    print("\033[91m" + "Eseguendo lo script bash..." + "\033[39m")
    execute(f'bash scripts/script-{i+1}.sh')
  
  return modified_text if remove else text

def create_event(text, token):
  matches = re.findall(filters['pattern_event'], text)
  if matches:
    for match in matches:
      try:
        title = match[0]
        date = match[1]
        time = match[2]

        event = {
          "title": title,
          "date": date,
          "time": time
        }
        new_event(event)
      except:
        speak("Non sono riuscito a creare l'evento")

    text = re.sub(filters['pattern_event'], '', text)
  else:
    speak("Non sono riuscito a creare l'evento")
  return text
  
def remove_history(text, token):
  with open("history.json", "w") as file:
    file.write("[]")
  return text.replace(token, '')


# TODO: verificare di essere nella repo git per evitare errori da git
def update(text, token):
  local = subprocess.run(["git", "rev-parse", "@"], capture_output=True, text=True).stdout.strip()
  remote = subprocess.run(["git", "rev-parse", "@{u}"], capture_output=True, text=True).stdout.strip()
  
  print("Local hash:  ", local)
  print("Remote hash: ", remote)
  
  if local == remote:
    speak("Non ho trovato aggiormamenti")
  else:
    subprocess.run(["chmod", "+x", "update.sh"])
    subprocess.Popen(["./update.sh"])
    
  return text.replace(token, '')

def set_timer(text, token):
  matches = re.findall(filters['pattern_timer'], text)
  if matches:
    for match in matches:
      try:
        id = int(match[0])
        seconds = int(match[1])

        if not start_timer(id, seconds):  # Imposta un timer
          print(f"Impossibile creare due timer con lo stesso id: {id}")

      except ValueError:
        print("time non impostato")

    text = re.sub(filters['pattern_timer'], '', text)
  return text
  
def set_volume(text, token):
  matches = re.findall(filters['pattern_volume'], text)
  if matches:
    for match in matches:
      try:
        percentage = int(match)
        set_master_volume(percentage)
        
      except ValueError:
        print("Errore nell'impostazione del volume")
    text = re.sub(filters['pattern_volume'], '', text)
  return text
                  
def get_timer_remaining(text, token):
  matches = re.findall(filters['pattern_remaining'], text)
  if matches:
    for match in matches:
      try:
        id = int(match)

        remaining = get_remaining(id)
        readable_time = convert_seconds_to_readable_time(remaining)

      except Exception as e:
        speak("Non sono riuscito ad ottenere informazioni sul timer")
        print("Exception:", e)

      if remaining != -1:
        text = re.sub(filters['pattern_remaining'], readable_time, text)
  return text
  
def _stop_timer(text, token):
  matches = re.findall(filters['pattern_stop_timer'], text)
  if matches:
    for match in matches:
      try:
        id = int(match)
        pid = _get_timer_pid(id)

        if pid != -1:
          if stop_timer(id):  # Interrompe il timer
            print(f"Timer id:{id} pid:{pid} interrotto")
          else:
            speak(f"Non ho trovato nessun timer con id {id}")
            print(f"Non ho trovato nessun timer con id {id}")
        else:
          speak("Non sono riuscito ad interrompere il timer")
          print("Non sono riuscito ad interrompere il timer")
      except ValueError:
        speak("Non sono riuscito ad interrompere il timer")

    text = re.sub(filters['pattern_stop_timer'], '', text)
  return text
  
def set_speed(text, token):
  matches = re.findall(filters['pattern_speed'], text)
  if matches:
    for match in matches:
      try:
        speed = float(match[0])

        print("VELOCITÀ IMPOSTATA A:", speed)

        # TODO: creare settings.py per controllare le impostazioni
        # Apre il file
        with open("settings.json", "r") as file:
          # Carica le impostazioni dal file
          settings = json.load(file)

          # Modifica la velocità di output
          settings['output_speed'] = speed

        with open("settings.json", "w") as file:
          # Salva le modifiche apportate
          json.dump(settings, file, indent=2)
        
      except Exception as e:
        speak("Non sono riuscito a modificare la velocità")
        print("Exception:", e)

    text = re.sub(filters['pattern_speed'], '', text)
  return text
  
def open_url(text, token):
  matches = re.findall(filters['pattern_url'], text)
  if matches:
    for url in matches:
      print("Apro l'url:", url)
      webbrowser.open(url)  # Apre l'url nel browser

    text = re.sub(filters['pattern_url'], '', text)
  return text

def async_post(url, data=None, params=None):
  kwargs = {
    'url': url,
    'params': params,
    'data': data
  }
  
  request = threading.Thread(target=requests.post, kwargs=kwargs)
  request.start()
  
def pause(text, token):
  async_post('http://127.0.0.1:5000/pause')
  return text.replace(token, '')

def resume(text, token):
  async_post('http://127.0.0.1:5000/resume')
  return text.replace(token, '')

def next_track(text, token):
  async_post('http://127.0.0.1:5000/next_track')
  return text.replace(token, '')

def prev_track(text, token):
  async_post('http://127.0.0.1:5000/prev_track')
  return text.replace(token, '')

def play_song(text, token):
  matches = re.findall(filters['pattern_play_song'], text)

  for name in matches:
    params = {
      'action': 'play',
      'query': name
    }
    async_post('http://127.0.0.1:5000/track', params=params)
  return re.sub(filters['pattern_play_song'], '', text)

def add_song_to_queue(text, token):
  matches = re.findall(filters['pattern_add_song_to_queue'], text)

  for name in matches:
    params = {
      'action': 'add_to_queue',
      'query': name
    }
    async_post('http://127.0.0.1:5000/track', params=params)
  return re.sub(filters['pattern_add_song_to_queue'], '', text)

def play_album(text, token):
  matches = re.findall(filters['pattern_play_album'], text)

  for name in matches:
    params = {
      'action': 'play',
      'query': name
    }
    async_post('http://127.0.0.1:5000/album', params=params)
  return re.sub(filters['pattern_play_album'], '', text)

def add_album_to_queue(text, token):
  matches = re.findall(filters['pattern_add_album_to_queue'], text)

  for name in matches:
    params = {
      'action': 'add_to_queue',
      'query': name
    }
    async_post('http://127.0.0.1:5000/album', params=params)
  return re.sub(filters['pattern_add_album_to_queue'], '', text)

def play_playlist(text, token):
  matches = re.findall(filters['pattern_play_playlist'], text)

  for name in matches:
    params = {
      'action': 'play',
      'query': name
    }
    async_post('http://127.0.0.1:5000/playlist', params=params)
  return re.sub(filters['pattern_play_playlist'], '', text)

def add_playlist_to_queue(text, token):
  matches = re.findall(filters['pattern_add_playlist_to_queue'], text)

  for name in matches:
    params = {
      'action': 'add_to_queue',
      'query': name
    }
    async_post('http://127.0.0.1:5000/playlist', params=params)
  return re.sub(filters['pattern_add_playlist_to_queue'], '', text)

def play_artist(text, token):
  matches = re.findall(filters['pattern_play_artist'], text)

  for name in matches:
    params = {
      'action': 'play',
      'query': name
    }
    async_post('http://127.0.0.1:5000/artist', params=params)
  return re.sub(filters['pattern_play_artist'], '', text)

def add_artist_to_queue(text, token):
  matches = re.findall(filters['pattern_add_artist_to_queue'], text)

  for name in matches:
    params = {
      'action': 'add_to_queue',
      'query': name
    }
    async_post('http://127.0.0.1:5000/artist', params=params)
  return re.sub(filters['pattern_add_artist_to_queue'], '', text)

def turn_on(text, token):
  matches = re.findall(filters['pattern_turn_on'], text)

  for _id in matches:
    power_on(_id)
    
  return re.sub(filters['pattern_turn_on'], '', text)

def turn_off(text, token):
  matches = re.findall(filters['pattern_turn_off'], text)

  for _id in matches:
    power_off(_id)
    
  return re.sub(filters['pattern_turn_off'], '', text)

def set_alarm(text, token):
  matches = re.findall(filters['pattern_alarm'], text)
  
  for match in matches:
    time = match[0]
    repeats = match[1] == 'true'

    start_alarm(time, repeats)
  return re.sub(filters['pattern_alarm'], '', text)

def _stop_alarm(text, token):
  matches = re.findall(filters['pattern_alarm'], text)
  
  for match in matches:
    time = match[0]
    stop_alarm(time)
  return re.sub(filters['pattern_alarm'], '', text)

functions = {
  # Sveglie
  '$SET_ALARM': set_alarm,
  '$STOP_ALARM': _stop_alarm,
  # Timer
  '$SET_TIMER': set_timer,
  '$STOP_TIMER': _stop_timer,
  '$GET_TIMER_REMAINING': get_timer_remaining,
  # Eventi
  '$NEW_EVENT': create_event,
  # Varie
  '$OPEN_URL': open_url,
  '$SET_SPEED': set_speed,
  '$REMOVE_HISTORY': remove_history,
  '$UPDATE': update,
  '$SET_MASTER_VOLUME': set_volume,
  '$TURN_ON_DEVICE': turn_on,
  '$TURN_OFF_DEVICE': turn_off,
  '$END': None,
  # Funzioni di Spotify
  '$PAUSE': pause,
  '$RESUME': resume,
  '$NEXT_TRACK': next_track,
  '$PREV_TRACK': prev_track,
  '$PLAY_SONG': play_song,
  '$PLAY_ARTIST': play_artist,
  '$PLAY_ALBUM': play_album,
  '$PLAY_PLAYLIST': play_playlist,
  '$ADD_SONG_TO_QUEUE': add_song_to_queue,
  '$ADD_ALBUM_TO_QUEUE': add_album_to_queue,
  '$ADD_PLAYLIST_TO_QUEUE': add_playlist_to_queue,
  '$ADD_ARTIST_TO_QUEUE': add_artist_to_queue
}

def replace_tokens(text):
  text = execute_and_remove_python_tags(text, remove=True)  # Esegue e rimuove gli script python
  text = execute_and_remove_code_blocks(text, remove=True)  # Esegue e rimuove gli script bash
  
  if '$END' in text:
    text = text.replace('$END', '')
    end = True
  else:
    end = False

  for token in functions:
    if token in text:
      text = functions[token](text, token)
  
  if end:
    text += '$END'
  return text

def remove_tokens(text):
  # *Rimuove i token riconosciuti per non leggerli ad alta voce
  
  timer_remaining = '$GET_TIMER_REMAINING'
  if timer_remaining in text:
    text = functions[timer_remaining](text, timer_remaining)
  
  for regex in filters:
    text = re.sub(filters[regex], '', text)
    
  for f in functions:
    text = text.replace(f, '')
  return text.strip()