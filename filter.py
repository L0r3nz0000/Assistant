from readable_time import convert_seconds_to_readable_time, get_readable_time, get_readable_date
from timer import start_timer, save_timer, stop_timer, _get_timer_pid, get_remaining
from events import new_event
from tts import speak
import webbrowser
import subprocess
import threading
import json
import os
import re

python_interpreter = "python3"

tokens = [
  '$TIME',
  '$DATE',
  '$SET_TIMER',
  '$STOP_TIMER',
  '$GET_TIMER_REMAINING',
  '$OPEN_URL',
  '$SET_SPEED',
  '$REMOVE_HISTORY',
  '$CHECK_UPDATES'
]

pattern_timer = r'\$SET_TIMER (\d+) (\d+)'                                            #   $SET_TIMER id seconds
pattern_stop_timer = r'\$STOP_TIMER (\d+)'                                            #   $STOP_TIMER id
pattern_remaining = r'\$GET_TIMER_REMAINING (\d+)'                                    #   $GET_TIMER_REMAINING id
pattern_speed = r'\$SET_SPEED (\d+(\.\d+)?)'                                          #   $SET_SPEED speed
pattern_url = r'\$OPEN_URL (\S+)'                                                     #   $OPEN_URL url
pattern_python = r'```python(.*?)```'                                                 #   ```python    code    ```
pattern_bash = r'```bash(.*?)```'                                                     #   ```bash      code    ```
pattern_event = r'\$NEW_EVENT\s+(\S+)\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{1,2})'  #   $NEW_EVENT titolo dd/mm/yyyy hh:mm

def execute(command):
  timer_thread = threading.Thread(target=subprocess.run, args=(command.split(),))
  timer_thread.start()

def execute_and_remove_python_tags(text, remove=False):
  # Estrai tutto il contenuto tra i tag python
  matches = re.findall(pattern_python, text, re.DOTALL)
  
  # Rimuovi i tag python dalla stringa originale
  modified_text = re.sub(pattern_python, '', text, flags=re.DOTALL)

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
  matches = re.findall(pattern_bash, text, re.DOTALL)
  
  # Rimuovi i blocchi di codice bash dalla stringa originale
  modified_text = re.sub(pattern_bash, '', text, flags=re.DOTALL)

  for match in matches:
    i = 0
    while os.path.exists(f'scripts/script-{i+1}.sh'):
      i += 1

    with open(f'scripts/script-{i+1}.sh', 'w') as file:
      file.write(match)
    print("\033[91m" + "Eseguendo lo script bash..." + "\033[39m")
    execute(f'bash scripts/script-{i+1}.sh')
  
  return modified_text if remove else text

def replace_tokens(text):
  text = execute_and_remove_python_tags(text, remove=True)  # Esegue e rimuove gli script python
  text = execute_and_remove_code_blocks(text, remove=True)  # Esegue e rimuove gli script bash

  for token in tokens:
    if token in text:
      if token == '$NEW_EVENT':
        matches = re.findall(pattern_event, text)
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

            text = re.sub(pattern_event, '', text)
        else:
          speak("Non sono riuscito a creare l'evento")
      
      elif token == '$REMOVE_HISTORY':
        with open("history.json", "w") as file:
          file.write("[]")
        text = text.replace(token, '')
      
      elif token == '$CHECK_UPDATES':
        local = subprocess.run(["git", "rev-parse", "@"], capture_output=True, text=True).stdout
        remote = subprocess.run(["git", "rev-parse", "@{u}"], capture_output=True, text=True).stdout
        
        print("Local:", local)
        print("Remote:", remote)

        if local == remote:
          speak("Non ho trovato aggiormamenti")
        else:
          subprocess.Popen(["chmod", "+x", "upgrade.sh", "&&", "./upgrade.sh"])
          speak("Sto scaricando gli aggiornamenti")
          
        text = text.replace(token, '')
        
      elif token == '$SET_TIMER':
        matches = re.findall(pattern_timer, text)
        if matches:
          for match in matches:
            try:
              id = int(match[0])
              seconds = int(match[1])

              if not start_timer(id, seconds):  # Imposta un timer
                print(f"Impossibile creare due timer con lo stesso id: {id}")
                speak("Non sono riuscito ad impostare il timer")

            except ValueError:
              speak("Non sono riuscito ad impostare il timer")

            text = re.sub(pattern_timer, '', text)
      
      elif token == '$GET_TIMER_REMAINING':
        matches = re.findall(pattern_remaining, text)
        if matches:
          for match in matches:
            try:
              id = int(match[0])

              remaining = get_remaining(id)
              readable_time = convert_seconds_to_readable_time(remaining)

            except Exception as e:
              speak("Non sono riuscito ad ottenere informazioni sul timer")
              print("Exception:", e)

            if remaining != -1:
              text = re.sub(pattern_remaining, readable_time, text)
      
      elif token == '$STOP_TIMER':
        matches = re.findall(pattern_stop_timer, text)
        if matches:
          for match in matches:
            try:
              id = int(match[0])
              pid = _get_timer_pid(id)

              if pid != -1:
                if stop_timer(id):  # Interrompe il timer
                  print(f"Timer id:{id} pid:{pid} interrotto")
                else:
                  speak(f"Non ho trovato nessun timer con id {id}")
              else:
                speak("Non sono riuscito ad interrompere il timer")
            except ValueError:
              speak("Non sono riuscito ad interrompere il timer")

            text = re.sub(pattern_stop_timer, '', text)
      
      elif token == '$SET_SPEED':
        matches = re.findall(pattern_speed, text)
        if matches:
          for match in matches:
            try:
              speed = float(match[0])

              print("VELOCITÀ IMPOSTATA A:", speed)

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

            text = re.sub(pattern_speed, '', text)

      elif token == '$OPEN_URL':
        matches = re.findall(pattern_url, text)
        if matches:
          for url in matches:
            print("Apro l'url:", url)
            webbrowser.open(url)  # Apre l'url nel browser

            text = re.sub(pattern_url, '', text)
      
      elif token == '$TIME':
        text = text.replace(token, get_readable_time())
      
      elif token == '$DATE':
        text = text.replace(token, get_readable_date())
  return text