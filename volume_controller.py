import subprocess

def get_playing_audio_apps():
  # Ottiene l'elenco dei sink input attivi (ossia le app che stanno riproducendo audio)
  result = subprocess.run(['pactl', 'list', 'sink-inputs'], stdout=subprocess.PIPE)
  output = result.stdout.decode()

  # Cattura gli ID dei sink input attivi
  sink_inputs = []
  for line in output.splitlines():
    if 'Sink Input #' in line:
      sink_id = line.split('#')[1]
      sink_inputs.append(sink_id)
  
  return sink_inputs

def set_volume(sink_id, volume):
  # Imposta il volume del sink input specificato
  subprocess.run(['pactl', 'set-sink-input-volume', sink_id, f'{volume}%'])