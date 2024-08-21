import subprocess

subprocess.Popen(['play', 'media/timer.mp3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("Sto facendo altre cose mentre l'audio viene riprodotto...")