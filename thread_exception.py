from threading import Thread
import ctypes
 
class StoppableThread(Thread):
  # Termina un thread invocando una exception
  def terminate(self):
    if not self.is_alive():
      return

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(self.ident), exc)
    if res == 0:
      raise ValueError("nonexistent thread id")
    elif res > 1:
      # if it returns a number greater than one, you're in trouble,
      # and you should call it again with exc=NULL to revert the effect
      ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, None)
      raise SystemError("PyThreadState_SetAsyncExc failed")