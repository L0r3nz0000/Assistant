import re
from datetime import datetime
from timer import set_timer
from tts import speak
from events import new_event
import webbrowser
import subprocess
import threading
import os

# Ottieni la data e l'ora corrente
now = datetime.now()

username = "lorenzo"
python_interpreter = "python3"

# Dizionari per i mesi e gli anni
months = {
  1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile",
  5: "maggio", 6: "giugno", 7: "luglio", 8: "agosto",
  9: "settembre", 10: "ottobre", 11: "novembre", 12: "dicembre"
}

years = {
  2020: "duemilaventi", 2021: "duemilaventuno", 2022: "duemilaventidue",
  2023: "duemilaventitré", 2024: "duemilaventiquattro", 2025: "duemilaventicinque",
  2026: "duemilaventisei"
}

# Ottieni la data corrente
now = datetime.now()

# Estrai giorno, mese, anno
giorno = now.day
month = months[now.month]
year = years[now.year]

# Crea la data in formato parole
date = f"{giorno} {month} {year}"

# Formatta l'ora come hh:mm
formatted_time = now.strftime("%H:%M")

tokens = {
  '$TIME': formatted_time,
  '$DATE': date,
  '$SET_TIMER': '',
  '$OPEN_URL': '',
  '[nome utente]': username
}

pattern_timer = r'\$SET_TIMER (\d+)'
pattern_url = r'\$OPEN_URL (\S+)'
pattern_python = r'```python(.*?)```'
pattern_bash = r'```bash(.*?)```'
pattern_event = r'\$NEW_EVENT\s+(\S+)\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{1,2})'

def execute(command):
  timer_thread = threading.Thread(target=subprocess.run, args=(command.split(),))
  timer_thread.start()

def execute_and_remove_python_tags(text):
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
  
  return modified_text

def execute_and_remove_code_blocks(text):
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
  
  return modified_text

def replace_tokens(text):
  text = execute_and_remove_python_tags(text)  # Esegue e rimuove gli script python
  text = execute_and_remove_code_blocks(text)  # Esegue e rimuove gli script bash

  for token in tokens:
    if token in text:
      if token == '$NEW_EVENT':
        matches = re.findall(pattern_event, text)
        if matches:
          for match in matches:
            title = match[0]
            date = match[1]
            time = match[2]

            event = {
              "title": title,
              "date": date,
              "time": time
            }
            new_event(event)

            text = re.sub(pattern_event, '', text)
        speak("Non sono riuscito a creare l'evento")


      if token == '$SET_TIMER':
        matches = re.findall(pattern_timer, text)
        if matches:
          for seconds in matches:
            try:
              seconds = int(seconds)
              
              set_timer(seconds)  # Imposta un timer
            except ValueError:
              speak("Non sono riuscito ad impostare il timer")

            text = re.sub(pattern_timer, '', text)

      elif token == '$OPEN_URL':
        matches = re.findall(pattern_url, text)
        if matches:
          for url in matches:
            print("Apro l'url:", url)
            webbrowser.open(url)  # Apre l'url nel browser

            text = re.sub(pattern_url, '', text)

      else:
        text = text.replace(token, tokens[token])
  return text