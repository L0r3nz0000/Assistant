from filter import replace_tokens
from datetime import datetime
import replicate
import json
import os

class ChatState:
  __BEGIN_TEXT__ =          "<|begin_of_text|>"
  __START_TURN_SYSTEM__ =   "<|start_header_id|>system<|end_header_id|>\n\n"
  __START_TURN_USER__  =    "<|start_header_id|>user<|end_header_id|>\n\n"
  __START_TURN_MODEL__ =    "<|start_header_id|>assistant<|end_header_id|>\n\n"
  __END_TURN__ =            "<|eot_id|>\n"

  llama3_1_405b = "meta/meta-llama-3.1-405b-instruct"
  llama3_70b =    "meta/meta-llama-3-70b-instruct"

  MODEL_NAME = llama3_70b
  HISTORY_FILE = "history.json"
  SETTINGS_FILE = "settings.json"

  def __init__(self, system="", history_json=[]):
    self.system_prompt = system
    self.history = []
    self.settings = {}
    self.history_json = history_json

    self._load_settings_from_file(self.SETTINGS_FILE)

    if len(history_json) == 0:
      print("Sto caricando la cronologia della chat dal file history.json")
      self._load_history_from_file(self.HISTORY_FILE)
    else:
      print("Sto caricando una cronologia custom")
      self._load_history_from_json()
  
  def _load_history_from_json(self):
    for interaction in self.history_json:
      if interaction["role"] == "user":
        self.history.append(self.__START_TURN_USER__ + interaction['timestamp'] + '\n' + interaction["message"] + self.__END_TURN__)
      elif interaction["role"] == "model":
        self.history.append(self.__START_TURN_MODEL__ + interaction['timestamp'] + '\n' + interaction["message"] + self.__END_TURN__)

  def _load_settings_from_file(self, file_path):
    if os.path.exists(file_path):
      with open(file_path, 'r') as file:
        self.settings = json.load(file)
  
  def _load_history_from_file(self, file_path):
    if os.path.exists(file_path):
      with open(file_path, 'r') as file:
        self.history_json = json.load(file)
      
      self._load_history_from_json()

  def _save_json_history(self, file_path):
    with open(file_path, 'w') as file:
      json.dump(self.history_json, file, indent=2)

  def add_to_history_as_user(self, message):
    """
    Adds a user message to the history with start/end turn markers.
    """
    now = datetime.now()
    
    timestamp = f'Timestamp: {now.strftime("%d/%m/%Y")} {now.strftime("%H:%M")}'
    self.history.append(self.__START_TURN_USER__ + timestamp + '\n' + message + self.__END_TURN__)

    self.history_json.append({
      "role": "user",
      "message": message,
      "timestamp": timestamp
    })

  def add_to_history_as_model(self, message):
    """
    Adds a model response to the history with start/end turn markers.
    """
    now = datetime.now()
    
    timestamp = f'Timestamp: {now.strftime("%d/%m/%Y")} {now.strftime("%H:%M")}'
    self.history.append(self.__START_TURN_MODEL__ + timestamp + '\n' + message + self.__END_TURN__)

    self.history_json.append({
      "role": "model",
      "message": message,
      "timestamp": timestamp
    })

  def get_history(self):
    """
    Returns the entire chat history as a single string.
    """
    return "".join([*self.history])

  def get_full_prompt(self):
    """
    Builds the prompt for the language model, including history and system description.
    """
    prompt = self.get_history() + self.__START_TURN_MODEL__
    if len(self.system_prompt)>0:
      prompt = self.__BEGIN_TEXT__ + self.__START_TURN_SYSTEM__ + self.system_prompt + self.__END_TURN__ + "\n" + prompt
    return prompt

  def send_message(self, message):
    self.add_to_history_as_user(message)
    prompt = self.get_full_prompt()

    input = {
      "prompt":         prompt,
      "max_tokens":     self.settings['max_tokens'],
      "min_tokens":     self.settings['min_tokens'],
      "temperature":    self.settings['temperature'],
      "length_penalty": self.settings['length_penalty']
    }

    response = ""

    try:
      for event in replicate.stream(self.MODEL_NAME, input=input):
        response += str(event)

    except replicate.exceptions.ReplicateError as e:
      print(e)
      exit(1)
    
    self.add_to_history_as_model(response)

    # Salva la risposta senza sostituire i token
    self._save_json_history(self.HISTORY_FILE)

    # Ritorna la risposta dopo aver sostituito i token
    return replace_tokens(response)