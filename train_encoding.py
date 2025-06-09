import face_recognition
import pickle
import os
import cv2

known_encodings = []
known_names = []

dataset_path = "known_faces"

for name in os.listdir(dataset_path):
    person_folder = os.path.join(dataset_path, name)
    if not os.path.isdir(person_folder):
        continue
    for filename in os.listdir(person_folder):
        image_path = os.path.join(person_folder, filename)
        image = cv2.imread(image_path)
        if image is None:
            continue
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb, model='hog')
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            known_encodings.append(encoding)
            known_names.append(name)

data = {"encodings": known_encodings, "names": known_names}

with open("encodings.pickle", "wb") as f:
    f.write(pickle.dumps(data))

print("[INFO] Encoding training complete.")
