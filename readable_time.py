from datetime import datetime

def convert_seconds_to_readable_time(seconds):
  # Calcola il numero di ore, minuti e secondi
  hours = seconds // 3600
  minutes = (seconds % 3600) // 60
  remaining_seconds = seconds % 60
  
  # Crea una lista per i componenti leggibili
  time_components = []
  
  if hours > 0:
    time_components.append(f"{hours} or{'e' if hours > 1 else 'a'}")
  if minutes > 0:
    time_components.append(f"{minutes} minut{'i' if minutes > 1 else 'o'}")
  if remaining_seconds > 0 or (hours == 0 and minutes == 0):
    time_components.append(f"{remaining_seconds} second{'i' if remaining_seconds > 1 and remaining_seconds != 0 else 'o'}")
  
  # Concatena i componenti in una stringa leggibile
  if hours > 0:
    readable_time = time_components[0] + ', ' + time_components[1] + ' e ' + time_components[2]
  else:
    readable_time = " e ".join(time_components)
  
  return readable_time