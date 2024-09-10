import socket

def send_wake_on_lan(mac_address):
  # Verifica che l'indirizzo MAC sia valido
  if len(mac_address) != 17 or not all(c in '0123456789ABCDEF:' for c in mac_address.upper()):
    raise ValueError("Indirizzo MAC non valido")

  # Converte l'indirizzo MAC in un formato binario
  mac_address = mac_address.upper().replace(":", "")
  mac_bytes = bytes.fromhex(mac_address)

  # Crea il pacchetto magic
  magic_packet = b'\xFF' * 6 + mac_bytes * 16

  # Invia il pacchetto magic via UDP
  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    # Imposta l'indirizzo di broadcast e la porta WOL
    broadcast_ip = '255.255.255.255'
    port = 9
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(magic_packet, (broadcast_ip, port))

  print("Pacchetto WOL inviato a", mac_address)