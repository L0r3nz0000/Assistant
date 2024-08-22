from filter import replace_tokens
import replicate
import json
import os

class ChatState():
  __BEGIN_TEXT__ = "<|begin_of_text|>"
  __START_TURN_SYSTEM__ = "<|start_header_id|>system<|end_header_id|>\n\n"
  __START_TURN_USER__ = "<|start_header_id|>user<|end_header_id|>\n\n"
  __START_TURN_MODEL__ = "<|start_header_id|>assistant<|end_header_id|>\n\n"
  __END_TURN__ = "<|eot_id|>\n"

  MODEL_NAME = "meta/meta-llama-3-70b-instruct"
  JSON_FILE = "history.json"

  def __init__(self, system=""):
    self.system_prompt = system
    self.history = []
    self.history_json = []

    self._load_history_from_json(self.JSON_FILE)
  
  def _load_history_from_json(self, file_path):
    if os.path.exists(file_path):
      with open(file_path, 'r') as file:
        self.history_json = json.load(file)
      
      for interaction in self.history_json:
        if interaction["role"] == "user":
          self.history.append(self.__START_TURN_USER__ + interaction["message"] + self.__END_TURN__)
        elif interaction["role"] == "model":
          self.history.append(self.__START_TURN_MODEL__ + interaction["message"] + self.__END_TURN__)

  def _save_json_history(self, file_path):
    with open(file_path, 'w') as file:
      json.dump(self.history_json, file, indent=2)

  def add_to_history_as_user(self, message):
    """
    Adds a user message to the history with start/end turn markers.
    """
    self.history.append(self.__START_TURN_USER__ + message + self.__END_TURN__)

    self.history_json.append({
      "role": "user",
      "message": message
    })

  def add_to_history_as_model(self, message):
    """
    Adds a model response to the history with start/end turn markers.
    """
    self.history.append(self.__START_TURN_MODEL__ + message + self.__END_TURN__)

    self.history_json.append({
      "role": "model",
      "message": message
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
      "prompt": prompt,
      "max_tokens": 1024,
      "min_tokens": 8
    }

    response = ""

    try:
      for event in replicate.stream(self.MODEL_NAME, input=input):
        response += str(event)

    except replicate.exceptions.ReplicateError as e:
      print(e)
      exit(1)

    response = replace_tokens(response)
    
    self.add_to_history_as_model(response)
    self._save_json_history(self.JSON_FILE)
    return response