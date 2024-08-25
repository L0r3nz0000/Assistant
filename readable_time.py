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
    time_components.append(f"{remaining_seconds} second{'i' if remaining_seconds > 1 else 'o'}")
  
  # Concatena i componenti in una stringa leggibile
  if hours > 0:
    readable_time = time_components[0] + ', ' + time_components[1] + ' e ' + time_components[2]
  else:
    readable_time = " e ".join(time_components)
  
  return readable_time

def get_readable_date():
  # Dizionari per i mesi e gli anni
  months = {
    1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile",
    5: "maggio", 6: "giugno", 7: "luglio", 8: "agosto",
    9: "settembre", 10: "ottobre", 11: "novembre", 12: "dicembre"
  }

  years = {
    2022: "duemilaventidue", 2023: "duemilaventitré", 2024: "duemilaventiquattro",
    2025: "duemilaventicinque", 2026: "duemilaventisei", 2027: "duemilaventisette",
    2028: "duemilaventotto", 2029: "duemilaventinove", 2030: "duemilatrenta",
  }

  # Ottieni la data corrente
  now = datetime.now()

  # Estrai giorno, mese, anno
  giorno = now.day
  month = months[now.month]
  year = years[now.year]

  # Crea la data in formato parole
  date = f"{giorno} {month} {year}"

def get_readable_time():
  now = datetime.now()
  # Formatta l'ora come hh:mm
  return now.strftime("%H:%M")