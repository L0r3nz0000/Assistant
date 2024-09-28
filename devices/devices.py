import paramiko
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from magic_packet import send_wake_on_lan

devices_path = os.path.join(os.path.dirname(__file__), 'devices.json')

def add_button(name: str, ip_address: str, _id: int):
  with open(devices_path, 'r') as file:
    devices = json.load(file)

  devices.append({
    'id': _id,
    'state': 'off',
    'name': name,
    'type': 'button',
    'ip_address': ip_address
  })

  with open(devices_path, 'w') as file:
    json.dump(devices, file)

def add_chromecast(friendly_name: str, uuid: str, _id: int, state: str = "off"):
  with open(devices_path, 'r') as file:
    devices = json.load(file)

  devices.append({
    'id': _id,
    'state': state,
    'uuid': uuid,
    'friendly_name': friendly_name,
    'type': 'chromecast'
  })

  with open(devices_path, 'w') as file:
    json.dump(devices, file)
    
def add_computer(name: str, ip_address: str, mac_address: str, username: str, password: str, _id: int):
  with open(devices_path, 'r') as file:
    devices = json.load(file)

  devices.append({
    'id': _id,
    'state': 'off',
    'name': name,
    'type': 'computer',
    'ip_address': ip_address,
    'mac_address': mac_address,
    'username': username,
    'password': password
  })

  with open(devices_path, 'w') as file:
    json.dump(devices, file)

def power_on(_id: int):
  """
  Accende un dispositivo.

  Parameters
  ----------
  _id : int
    L'id del dispositivo da accendere.
  """
  from filter import async_post
  with open(devices_path, 'r') as file:
    devices = json.load(file)

  for device in devices:
    if device['id'] == _id:
      
      match device['type']:
        case 'button':
          device['state'] = 'on'
          # TODO: implementare un autenticazione per accendere e spegnere le luci
          async_post(f'http://{device["ip_address"]}/power_on')
          
        case 'computer':
          device['state'] = 'on'
          magic_packet.send_wake_on_lan(device['mac_address'])
          
        case _:
          pass

  with open(devices_path, 'w') as file:
    json.dump(devices, file)

def ssh_shutdown(hostname, username, password):
  import subprocess
  try:
    comando_spegnimento = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no {username}@{hostname} 'echo \'{password}\' | sudo shutdown -h now'"
    
    subprocess.Popen(comando_spegnimento, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  except Exception as e:
    print(f"Errore durante la connessione o l'esecuzione del comando: {e}")


def power_off(_id: int):
  """
  Spegne il dispositivo con l'id specificato.
  
  Parameters
  ----------
  _id : int
    L'id del dispositivo da spegnere.
  """
  from filter import async_post
  with open(devices_path, 'r') as file:
    devices = json.load(file)
  
  for device in devices:
    if device['id'] == _id:
      
      match device['type']:
        case 'button':
          device['state'] = 'off'
          async_post(f'http://{device["ip_address"]}/power_off')
          
        case 'computer':
          device['state'] = 'off'
          # TODO: provare lo spegnimento del computer tramite ssh
          ssh_shutdown(device['ip_address'], device['username'], device['password'])
          
        case _:
          pass

def get_all_devices():
  with open(devices_path, 'r') as file:
    devices = json.load(file)

  return devices

def get_device(_id: int):
  devices = get_all_devices()

  for device in devices:
    if device['id'] == _id:
      return device
  return None

def interactive_add_device():
  print(
"""Benvenuto nello script per collegare un dispositivo all'assistente vocale
Scegli un tipo di dispositivo da aggiungere tra quelli compatibili:
\t1. Computer
\t2. Button""")
  
  try:
    type = int(input("> "))
    if type != 1 and type != 2:
      raise ValueError
    else:
      type = 'computer' if type == 1 else 'button'
  except ValueError:
    print("Valore non valido")
  
  with open(devices_path, 'r') as file:
    devices = json.load(file)
  
  if devices:
    _id = devices[-1]['id'] + 1
  else:
    _id = 0

  name = input("Inserisci il nome del dispositivo: ")
  ip_address = input("Inserisci l'indirizzo IP del dispositivo: ")
  
  if type == 'computer':
    mac_address = input("Inserisci l'indirizzo MAC del dispositivo: ")
    username = input("Inserisci lo username del dispositivo (verrà utilizzato per spegnere il dispositivo tramite ssh): ")
    password = input("Inserisci la password del dispositivo (verrà utilizzata per spegnere il dispositivo tramite ssh): ")

    add_computer(name, ip_address, mac_address, username, password, _id)
    
  elif type == 'button':
    add_button(name, ip_address, _id)

if __name__ == '__main__':
  interactive_add_device()