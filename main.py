from wake_word import wake_word_callback, blocking_wake_word
from ChatState import ChatState
from stt import listen_prompt
import multiprocessing
from tts import speak

def new_interaction(chat, conversation_open, response_completed):
  user_prompt = listen_prompt()

  process = multiprocessing.Process(target=interaction, args=(chat, user_prompt, conversation_open, response_completed))
  process.start()
  return process

def interaction(chat, user_prompt, conversation_open, response_completed):
  response_completed.clear()

  if user_prompt:
    print('\033[94m' + 'User:' + '\033[39m', user_prompt)

    output = chat.send_message(user_prompt).strip()
    print('\033[94m' + 'Model:' + '\033[39m', output)

    if output:
      if '$END' in output:
        # La conversazione è chiusa
        conversation_open.clear()
        output = output.replace('$END', '')
      else:
        # La conversazione continua
        conversation_open.set()
      
      speak(output)
  else:
    speak("Scusa, non ho capito.")
    conversation_open.clear()
  response_completed.set()

if __name__ == "__main__":
  conversation_open = multiprocessing.Event()  # Default False
  response_completed = multiprocessing.Event()

  with open("system_prompt.txt", "r") as file:
    system_prompt = file.read()
  
  chat = ChatState(system=system_prompt)
  
  wake_word_callback(new_interaction, conversation_open, response_completed, (chat, conversation_open, response_completed))