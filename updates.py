from stt import listen_prompt
from tts import speak
import subprocess

def fetch_updates(update_available):
  while True:
    subprocess.run(["git", "fetch"])
    local = subprocess.run(["git", "rev-parse", "@"], capture_output=True, text=True).stdout.strip()
    remote = subprocess.run(["git", "rev-parse", "@{u}"], capture_output=True, text=True).stdout.strip()
    if local != remote:
      update_available.set()
      break