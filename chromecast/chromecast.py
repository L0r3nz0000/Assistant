import pychromecast
import zeroconf
import time

class CustomChromecastManager():
  devices = []
  def __init__(self):
    pass
  
  def get_chromecasts(self):
    return self.devices
  
  def discovery_chromecasts(self, sleep=2):
    def _add_device(uuid, service):
      # Se il dispositivo non è già nell'elenco lo aggiunge (per evitare dispositivi doppi)
      if not any(device['uuid'] == uuid for device in self.devices):
        d = {'uuid': str(uuid), 'name': browser.devices[uuid].friendly_name}
        self.devices.append(d)
      
    zconf = zeroconf.Zeroconf()
    browser = pychromecast.CastBrowser(pychromecast.SimpleCastListener(_add_device), zconf)
    browser.start_discovery()
    time.sleep(3)
    pychromecast.discovery.stop_discovery(browser)

if __name__ == "__main__":
  manager = CustomChromecastManager()
  manager.discovery_chromecasts()
  print(manager.get_chromecasts())