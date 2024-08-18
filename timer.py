from sounds import async_sound

def set_timer(seconds):
  async_sound("media/timer.mp3", delay=seconds)