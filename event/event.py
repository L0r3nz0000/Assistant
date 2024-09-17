import json
import os

events_path = os.path.join(os.path.dirname(__file__), 'events.json')

def load_events(file_path):
  # Apri il file e carica il contenuto
  with open(file_path, 'r') as file:
    return json.load(file)

def new_event(event):
  events = []
  if os.path.exists(events_path):
    events = load_events(events_path)
  
  events.append(event)
  
  with open(events_path, 'w') as file:
    json.dump(events, file, indent=2)

def delete_event(title):
  events = []
  if os.path.exists(events_path):
    events = load_events(events_path)
  
  for event in events:
    if event['title'] == title:
      events.remove(event)
  
  with open(events_path, 'w') as file:
    json.dump(events, file, indent=2)