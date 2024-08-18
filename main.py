import replicate
from tts import speak
from sounds import async_sound
from stt import listen_prompt
from filter import replace_tokens
from ChatState import ChatState
from time import sleep
from wake_word import listen_for_wake_word

chat = ChatState(system="""Sei un chatbot vocale in grado di avere conversazioni follow-up con l'utente, termina la conversazione appena possibile usando $END a meno che tu non debba chiedere qualcosa all'utente. Oltre alle normali risposte hai a disposizione dei tag che puoi inserire solo in caso di necessità nelle risposte per richiamare funzioni ed inserire informazioni nella frase:
$TIME -> viene sostituito con l'orario attuale, per esempio "Sono le $TIME $END"
$DATE -> per la data, per esempio "Oggi è il $DATE $END"
$SET_TIMER secondi -> imposta un timer, per esempio "$SET_TIMER 60 Ho impostato un timer di un minuto"
$OPEN_URL url -> apre un link nel browser, per esempio Sto aprendo il sito di google $OPEN_URL https://www.google.com
$NEW_EVENT titolo dd/mm/yyyy hh:mm -> crea un nuovo evento nel calendario, per esempio "Ho creato un evento domani $NEW_EVENT festa 18/08/2024 20:30"
$END -> termina la conversazione, per esempio "output... $END"
Se vuoi eseguire codice puoi usare questi tag:
per il codice python
```python
print("hello world")
```
per il codice bash
```bash
echo "ciao"
```
in tutti e due i casi il codice verrà eseguito automaticamente nel computer dell'utente.
""")

conversation_open = False

while True:
  if not conversation_open:
    listen_for_wake_word()
  
  user_prompt = listen_prompt()

  if user_prompt:
    print('\033[94m' + 'User:' + '\033[39m', user_prompt)

    output = chat.send_message(user_prompt).strip()
    print('\033[94m' + 'Model:' + '\033[39m', output)

    if output:
      if '$END' in output:
        # La conversazione è chiusa
        conversation_open = False
        output = output.replace('$END', '')
      else:
        # La conversazione continua
        conversation_open = True
      speak(output)
  else:
    speak("Scusa, non ho capito.")
    conversation_open = False