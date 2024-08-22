import sys
import os

# Reindirizza temporaneamente sys.stderr
def suppress_stderr():
  stderr_fileno = sys.stderr.fileno()
  old_stderr = os.dup(stderr_fileno)
  devnull = os.open(os.devnull, os.O_WRONLY)
  os.dup2(devnull, stderr_fileno)
  os.close(devnull)
  return old_stderr

# Ripristina sys.stderr
def restore_stderr(old_stderr):
  stderr_fileno = sys.stderr.fileno()
  os.dup2(old_stderr, stderr_fileno)
  os.close(old_stderr)