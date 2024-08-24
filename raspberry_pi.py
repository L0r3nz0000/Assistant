import os

def is_raspberry_pi():
  try:
    # Verifica dell'esistenza del file specifico del Raspberry Pi
    if os.path.exists('/proc/device-tree/model'):
      with open('/proc/device-tree/model', 'r') as f:
        model = f.read().lower()
        
        return 'raspberry pi' in model
  except Exception as e:
    print(f"Errore durante il controllo: {e}")

  return False