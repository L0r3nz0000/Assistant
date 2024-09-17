import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pychromecast
from devices import get_all_devices, add_chromecast, get_device
import zeroconf
import time

class CustomChromecastManager():
  def __init__(self):
    self.cast = None
    self.mc = None
    self.devices = []
  
  def get_chromecasts(self):
    return self.devices
  
  def discovery_chromecasts(self, sleep=3):
    def _device_exists(uuid):
      devices = get_all_devices()
      for device in devices:
        if device['type'] == 'chromecast':
          if device['uuid'] == uuid:
            return True
      return False
    
    def _add_device(uuid, service):
      # Se il dispositivo non è già nell'elenco lo aggiunge (per evitare dispositivi doppi)
      if not _device_exists(str(uuid)):
        devices = get_all_devices()
        
        # Determina l'identificativo della chromecast
        _id = devices[-1]['id'] + 1 if len(devices) else 0
        friendly_name = browser.devices[uuid].friendly_name
        
        # TODO: passare lo stato del dispositivo (on/off)
        add_chromecast(friendly_name, str(uuid), _id)
        
        d = {'id': _id, 'uuid': str(uuid), 'friendly_name': friendly_name}
        self.devices.append(d)
      
    zconf = zeroconf.Zeroconf()
    browser = pychromecast.CastBrowser(pychromecast.SimpleCastListener(_add_device), zconf)
    browser.start_discovery()
    time.sleep(sleep)
    pychromecast.discovery.stop_discovery(browser)
  
  def connect_chromecast(self, _id):
    device = get_device(_id)
    if device:
      if device['type'] == 'chromecast':
        chromecasts, browser = pychromecast.get_listed_chromecasts(uuids=[device['uuid']])
    
        if len(chromecasts) > 0:
          self.cast = chromecasts[0]
          self.mc = self.cast.media_controller
          print('Chromecast connesso')
      else:
        print(f'Il dispositivo {_id} è un {device["type"]}')
    else:
      print('Dispositivo non trovato')
  
  def pause(self):
    if self.mc:
      self.mc.pause()
  
  def play(self):
    if self.mc:
      self.mc.play()
  
  def set_volume(self, volume):
    if self.cast:
      self.cast.set_volume(volume)
      
if __name__ == "__main__":
  manager = CustomChromecastManager()
  manager.discovery_chromecasts()
  print(manager.get_chromecasts())
  #manager.connect_chromecast(1)