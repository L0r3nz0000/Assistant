from stt import listen_prompt
from tts import speak
import subprocess

def fetch_updates(update_available):
  subprocess.run(["git", "fetch"])
  local = subprocess.run(["git", "rev-parse", "@"], capture_output=True, text=True).stdout.strip()
  remote = subprocess.run(["git", "rev-parse", "@{u}"], capture_output=True, text=True).stdout.strip()
  print("aggiornamnti:", local != remote)
  if local != remote: update_available.set()
  
def ask_for_updates(chat):
  question = "Ciao, è disponibile un aggiornamento, vuoi farlo ora?"
  speak(question)
  
  chat.add_to_history_as_model(question)
  
  # Aspetta la risposta dell'utente
  prompt = listen_prompt()
  return prompt#chat.send_message(prompt)