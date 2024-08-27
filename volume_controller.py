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
  subprocess.Popen(['pactl', 'set-sink-input-volume', sink_id, f'{volume}%'], stdout=subprocess.PIPE)

def set_master_volume(volume):
  if volume >= 0 and volume <= 100:
    subprocess.Popen(["amixer", "sset", "'Master'", f"{volume}%"], stdout=subprocess.PIPE)
  else:
    print("Invalid parameter volume:", volume)