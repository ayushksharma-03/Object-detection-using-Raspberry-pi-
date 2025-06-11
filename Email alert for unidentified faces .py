import cv2
import face_recognition
import pickle
import time
import os
import datetime
import yagmail
from picamera2 import Picamera2

# Load face encodings
with open("encodings.pickle", "rb") as f:
    data = pickle.load(f)

# Load Haar Cascade
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Init Pi Camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

# Ensure intruder_logs directory exists
os.makedirs("intruder_logs", exist_ok=True)

# Email config
SENDER_EMAIL = "your_email@gmail.com"
APP_PASSWORD = "your_app_password"
RECEIVER_EMAIL = "recipient@example.com"

yag = yagmail.SMTP(SENDER_EMAIL, APP_PASSWORD)

# Alert tracking
unknown_start_time = None
unknown_triggered = False

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    encodings = face_recognition.face_encodings(rgb)

    names = []
    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"

        if True in matches:
            matched_idxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            for i in matched_idxs:
                counts[data["names"][i]] = counts.get(data["names"][i], 0) + 1
            name = max(counts, key=counts.get)

        names.append(name)

    for ((x, y, w, h), name) in zip(faces, names):
        cv2.rectangle(frame, (x, y), (x + w, y + h),
                      (0, 255, 0) if name != "Unknown" else (0, 0, 255), 2)
        cv2.putText(frame, name, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        if name == "Unknown":
            if not unknown_start_time:
                unknown_start_time = time.time()
            elif time.time() - unknown_start_time >= 10 and not unknown_triggered:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"intruder_logs/intruder_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"[ALERT] Unknown person detected. Image saved: {filename}")

                # Send email with attachment
                try:
                    yag.send(
                        to=RECEIVER_EMAIL,
                        subject="🔔 Intruder Alert!",
                        contents="An unknown person was detected by your Raspberry Pi security system.",
                        attachments=filename
                    )
                    print("[EMAIL] Alert sent successfully.")
                except Exception as e:
                    print(f"[ERROR] Failed to send email: {e}")

                unknown_triggered = True
        else:
            unknown_start_time = None
            unknown_triggered = False

    cv2.imshow("Security Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.close()
