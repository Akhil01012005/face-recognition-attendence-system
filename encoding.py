import cv2
import pickle
import os
import face_recognition
from pymongo import MongoClient
import gridfs

# MongoDB Connection
client = MongoClient("mongodb+srv://dasariakhil:201022539002@cluster0.lonxb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['LFDCAttendence']
fs = gridfs.GridFS(db)

# Folder containing student images
folder_path = "C:\\Users\\Akhil Dasari\\facerecognition\\images"
path_list = os.listdir(folder_path)

image_list = []
student_ids = []

for path in path_list:
    image_path = os.path.join(folder_path, path)
    image = cv2.imread(image_path)

    if image is None:
        print(f"⚠️ Could not read image: {image_path}")
        continue

    # Add image to list
    image_list.append(image)

    # Extract student ID from filename (without extension)
    student_id = os.path.splitext(path)[0]
    student_ids.append(student_id)
 
    # Upload image to GridFS
    with open(image_path, "rb") as img_file:
        file_id = fs.put(img_file, filename=path)
        print(f"📤 Image '{path}' uploaded successfully to GridFS with ID: {file_id}")

print("✅ All student IDs collected:", student_ids)

# Encode faces
def find_encodings(images, student_ids):
    encode_list = []
    valid_ids = []

    for img, sid in zip(images, student_ids):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodes = face_recognition.face_encodings(img_rgb)
        
        if encodes:
            encode_list.append(encodes[0])
            valid_ids.append(sid)
        else:
            print(f"⚠️ No face found in image of student ID: {sid}, skipping...")

    return encode_list, valid_ids

print("🔍 Encoding started...")
encode_list_known, valid_ids = find_encodings(image_list, student_ids)
print("✅ Encoding completed.")

# Save encodings and corresponding student IDs
data = [encode_list_known, valid_ids]
with open("EncodeFile.p", "wb") as file:
    pickle.dump(data, file)

print("💾 EncodeFile.p saved successfully.")
