
import cv2

# Apriamo la fotocamera
cap = cv2.VideoCapture(0)

while True:
    # Leggiamo un frame dalla fotocamera
    ret, frame = cap.read()
    
    # Se il frame è stato letto correttamente, lo visualizziamo
    if ret:
        cv2.imshow('Fotocamera', frame)
    
    # Se premiamo il tasto 'q', chiudiamo l'applicazione
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Chiudiamo la fotocamera e la finestra
cap.release()
cv2.destroyAllWindows()
