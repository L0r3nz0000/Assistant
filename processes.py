import psutil

def kill_process_and_children(pid):
  try:
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
      child.terminate()  # Invia SIGTERM ai figli
    parent.terminate()  # Invia SIGTERM al processo padre

    # Attendi che i processi vengano terminati
    _, still_alive = psutil.wait_procs(children, timeout=5)
    for child in still_alive:
      child.kill()  # Invia SIGKILL ai figli che non si sono chiusi
    parent.kill()  # Invia SIGKILL al processo padre se non si è chiuso
  except psutil.NoSuchProcess:
    pass