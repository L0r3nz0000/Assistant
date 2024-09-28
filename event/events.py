import json
import os

file_path = 'events.json'

def load_events(file_path):
  # Apri il file e carica il contenuto
  with open(file_path, 'r') as file:
    return json.load(file)

def new_event(event):
  events = []
  if os.path.exists(file_path):
    events = load_events(file_path)
  
  events.append(event)
  
  with open(file_path, 'w') as file:
    json.dump(events, file, indent=2)