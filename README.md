import cv2
from picamera2 import Picamera2

# Initialize Pi Camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

# OpenCV window loop
while True:
    frame = picam2.capture_array()
    cv2.imshow("Raspberry Pi Camera", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cv2.destroyAllWindows()
picam2.close()
