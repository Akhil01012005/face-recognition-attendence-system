import cv2
import os
import pickle
import face_recognition
import numpy as np
from pymongo import MongoClient
from datetime import datetime, timezone
import threading
import playsound
import pytz

# MongoDB Connection
client = MongoClient("mongodb+srv://dasariakhil:201022539002@cluster0.lonxb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['LFDCAttendence']
collection = db['Datascience']

# Timezone Setup (Asia/Kolkata)
TIMEZONE = pytz.timezone("Asia/Kolkata")

# Load camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load background image
bg_path = "C:\\Users\\Akhil Dasari\\facerecognition\\resources\\background\\background.jpg"
imgBackground = cv2.imread(bg_path)

if imgBackground is None:
    print(f"❌ ERROR: Background image not found at {bg_path}. Check the path.")
    exit()

def play_sound(sound_path):
    threading.Thread(target=playsound.playsound, args=(sound_path,), daemon=True).start()

# Load mode images
folderModePath = "resources/modes"
modePathList = os.listdir(folderModePath)

imageModeList = []
for path in modePathList:
    img = cv2.imread(os.path.join(folderModePath, path))
    if img is not None:
        img_resized = cv2.resize(img, (414, 633))
        imageModeList.append(img_resized)

if len(imageModeList) < 4:
    print(f"⚠️ Warning: Expected at least 4 mode images, but found {len(imageModeList)}.")

print("✅ Mode images loaded:", len(imageModeList))

# Load encodings
print("🔍 Loading encode file...")
with open("EncodeFile.p", "rb") as file:
    encodeListKnown, studentIds = pickle.load(file)
print("✅ Encode file loaded")

# Initialize variables
modeType = 0
counter = 0
Id = -1
student_data = None
sound_played = False
last_detected_id = None

# Play initial sound
play_sound("C:\\Users\\Akhil Dasari\\Downloads\\zapsplat_science_fiction_computer_tone_beep_positive_accepted_83987.mp3")

# Function to get current time in ISO 8601 format
def get_current_time():
    current_time_utc = datetime.now(timezone.utc)
    current_time_local = current_time_utc.astimezone(TIMEZONE)
    return current_time_local.isoformat()

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img

    # --- Mode 0: Ready to Scan ---
    if modeType == 0:
        imgBackground[44:44 + 633, 808:808 + 414] = imageModeList[2]

        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                Id = str(studentIds[matchIndex])
                print("✅ Face Matched. ID:", Id)

                student_data = collection.find_one({"_id": Id})
                current_time = get_current_time()

                if student_data:
                    last_att_time_str = student_data.get('last_attendance_time', '')

                    if last_att_time_str:
                        try:
                            last_att_time = datetime.fromisoformat(last_att_time_str).astimezone(TIMEZONE)
                            current_time_obj = datetime.fromisoformat(current_time).astimezone(TIMEZONE)
                            secondsDiff = (current_time_obj - last_att_time).total_seconds()
                        except ValueError as e:
                            print(f"⚠️ Error converting time: {e}")
                            secondsDiff = None
                    else:
                        secondsDiff = None

                    if secondsDiff is None or secondsDiff > 1000:
                        student_data['total_attendance'] += 1

                        collection.update_one({"_id": Id}, {
                            "$set": {
                                "total_attendance": student_data['total_attendance'],
                                "last_attendance_time": current_time
                            },
                            "$push": {
                                "attendance_time_log": current_time
                            }
                        })

                        modeType = 1
                    else:
                        print(f"⏳ Too soon. Last attendance: {student_data['last_attendance_time']}")
                        modeType = 3

                    counter = 0
                    break

                else:
                    print("❌ No student data found in MongoDB for ID:", Id)
                    modeType = 4  # Unknown Student
                    counter = 0
                    break

    # --- Mode 1: Show Student Info ---
    elif modeType == 1:
        imgBackground[44:44 + 633, 808:808 + 414] = imageModeList[3]

        face_path = f"images/{Id}.jpg"
        if os.path.exists(face_path):
            imgStudent = cv2.imread(face_path)
            imgStudent = cv2.resize(imgStudent, (250, 250))
            imgBackground[180:430, 900:1150] = imgStudent
        else:
            print("⚠️ No face image found for student:", Id)

        if student_data:
            text_x = 950
            image_top = 430
            line_spacing = 40

            cv2.putText(imgBackground, student_data['name'], (text_x, image_top + line_spacing),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(imgBackground, f"Group: {student_data['group']}", (text_x, image_top + 2 * line_spacing),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(imgBackground, f"ID: {student_data['_id']}", (text_x, image_top + 3 * line_spacing),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(imgBackground, f"Year: {student_data['year']}", (text_x, image_top + 4 * line_spacing),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (225, 225, 225), 1)
            cv2.putText(imgBackground, f"TP: {student_data['total_attendance']}", (861, 125),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)

            formatted_time = datetime.now().strftime("%I:%M:%S %p")
            cv2.putText(imgBackground, formatted_time, (1050, 150),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)

        counter += 1
        if counter >= 6:
            modeType = 2
            counter = 0

    # --- Mode 2: End Message ---
    elif modeType == 2:
        imgBackground[44:44 + 633, 808:808 + 414] = imageModeList[0]

        if Id != last_detected_id or last_detected_id is None:
            last_detected_id = Id
            sound_played = False

        if not sound_played and last_detected_id == Id:
            play_sound("c:\\Users\\Akhil Dasari\\Downloads\\p_42214563_35.mp3")
            sound_played = True

        counter += 1
        if counter >= 6:
            modeType = 0
            counter = 0
            Id = -1
            student_data = None

    # --- Mode 3: Too Soon Warning ---
    elif modeType == 3:
        imgBackground[44:44 + 633, 808:808 + 414] = imageModeList[1]

        if Id != last_detected_id or last_detected_id is None:
            last_detected_id = Id
            sound_played = False

        if not sound_played and last_detected_id == Id:
            play_sound("C:\\Users\\Akhil Dasari\\Downloads\\p_42214596_91.mp3")
            sound_played = True

        counter += 1
        if counter >= 6:
            modeType = 0
            counter = 0
            Id = -1
            student_data = None

    # --- Mode 4: Unknown Student ---
    elif modeType == 4:
        imgBackground[44:44 + 633, 808:808 + 414] = imageModeList[1]  # Optional: Add separate image for unknown

        if not sound_played:
            play_sound("C:\\Users\\Akhil Dasari\\Downloads\\unknown_student_alert.mp3")
            sound_played = True

        cv2.putText(imgBackground, "❌ Student Not Found", (850, 700),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 255), 2)

        counter += 1
        if counter >= 6:
            modeType = 0
            counter = 0
            Id = -1
            student_data = None

    cv2.imshow("Face Attendance", imgBackground)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
