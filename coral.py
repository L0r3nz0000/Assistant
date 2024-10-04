import cohere
from datetime import datetime
import json
import os

class CoralChat:
  MODEL_NAME = "command-r-plus-08-2024"
  HISTORY_FILE = "history.json"
  SETTINGS_FILE = "settings.json"

  def __init__(self, system="", history_json=[]):
    self.system_prompt = system
    self.history = []
    self.settings = {}
    self.history_json = history_json
    
    self.co = cohere.Client()
    print("Ready!")

    self._load_settings_from_file(self.SETTINGS_FILE)

    if len(history_json) == 0:
      print("Sto caricando la cronologia della chat dal file history.json")
      self._load_history_from_file(self.HISTORY_FILE)
    else:
      print("Sto caricando una cronologia custom")
      self._load_history_from_json()
  
  def _load_history_from_json(self):
    
    for interaction in self.history_json:
      if interaction["role"] == "USER":
        self.history.append({"role": "USER", "message": interaction["message"]})
      elif interaction["role"] == "CHATBOT":
        self.history.append({"role": "CHATBOT", "message": interaction["message"]})

  def _load_settings_from_file(self, file_path):
    if os.path.exists(file_path):
      with open(file_path, 'r') as file:
        self.settings = json.load(file)
  
  def _load_history_from_file(self, file_path):
    if os.path.exists(file_path):
      with open(file_path, 'r') as file:
        self.history_json = json.load(file)
      
      self._load_history_from_json()

  def _save_json_history(self):
    with open(self.HISTORY_FILE, 'w') as file:
      json.dump(self.history_json, file, indent=2)

  def add_to_history_as_user(self, message):
    """
    Adds a user message to the history with start/end turn markers.
    """
    now = datetime.now()
    
    timestamp = f'Timestamp: {now.strftime("%d/%m/%Y")} {now.strftime("%H:%M")}'

    self.history_json.append({
      "role": "USER",
      "message": message,
      "timestamp": timestamp
    })
    
    self.history.append({
      "role": "USER",
      "message": message
    })
    
    self._save_json_history()

  def add_to_history_as_model(self, message):
    """
    Adds a model response to the history with start/end turn markers.
    """
    self.history_json.append({
      "role": "CHATBOT",
      "message": message
    })
    
    self.history.append({
      "role": "CHATBOT",
      "message": message
    })
    
    self._save_json_history()

  def send_message(self, message):
    self.add_to_history_as_user(message)
    
    now = datetime.now()
    
    timestamp = f'Timestamp: {now.strftime("%d/%m/%Y")} {now.strftime("%H:%M")}'
    message = timestamp + "\n" + message
    
    print("Sending:", message)

    input = {
      "model":            self.MODEL_NAME,
      "message":          message,
      "temperature":      self.settings['temperature'],
      "chat_history":     self.history,
      "preamble":         self.system_prompt
    }
    
    try:
      # ritorna il generatore per ottenere la risposta
      return self.co.chat_stream(**input)

    except cohere.core.api_error.ApiError as e:
      print(e)
      exit(1)
      

if __name__ == "__main__":
  with open("system_prompt.txt", "r") as file:
    sys_prompt = file.read()
    
  chat = CoralChat(system=sys_prompt)
  stream = chat.send_message("spegni il computer")
  
  response = ""
  for event in stream:
    if event.event_type == "text-generation":
      print(event.text, end='', flush=True)
      response += event.text
  
  chat.add_to_history_as_model(response)