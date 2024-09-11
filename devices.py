from magic_packet import send_wake_on_lan
from filter import async_post, execute
import json

def add_button(name: str, ip_address: str, _id: int):
  with open('devices.json', 'r') as file:
    devices = json.load(file)

  devices.append({
    'id': _id,
    'state': 'off',
    'name': name,
    'type': 'button',
    'ip_address': ip_address
  })

  with open('devices.json', 'w') as file:
    json.dump(devices, file)
    
def add_computer(name: str, ip_address: str, mac_address: str, password: str, _id: int):
  with open('devices.json', 'r') as file:
    devices = json.load(file)

  devices.append({
    'id': _id,
    'state': 'off',
    'name': name,
    'type': 'computer',
    'ip_address': ip_address,
    'mac_address': mac_address,
    'password': password
  })

  with open('devices.json', 'w') as file:
    json.dump(devices, file)

def power_on(_id: int):
  with open('devices.json', 'r') as file:
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
          send_wake_on_lan(device['mac_address'])
          
        case _:
          pass

  with open('devices.json', 'w') as file:
    json.dump(devices, file)

def power_off(_id: int):
  with open('devices.json', 'r') as file:
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
          execute(f'sshpass -p "{device["password"]}" ssh -o StrictHostKeyChecking=no {device["ip_address"]} "echo \'{device["password"]}\' | sudo -S shutdown -h now"')
          
        case _:
          pass

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
  
  with open('devices.json', 'r') as file:
    devices = json.load(file)
  
  if devices:
    _id = devices[-1]['id'] + 1
  else:
    _id = 0

  name = input("Inserisci il nome del dispositivo: ")
  ip_address = input("Inserisci l'indirizzo IP del dispositivo: ")
  
  if type == 'computer':
    mac_address = input("Inserisci l'indirizzo MAC del dispositivo: ")
    password = input("Inserisci la password del dispositivo (verrà utilizzata per spegnere il dispositivo tramite ssh): ")

    add_computer(name, ip_address, mac_address, password, _id)
    
  elif type == 'button':
    add_button(name, ip_address, _id)

if __name__ == '__main__':
  interactive_add_device()