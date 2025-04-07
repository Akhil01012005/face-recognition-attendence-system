from pymongo import MongoClient
from datetime import datetime
import pytz

# 🎯 Connect to MongoDB
client = MongoClient("mongodb+srv://dasariakhil:201022539002@cluster0.lonxb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["LFDCAttendence"]
collection = db["Datascience"]

# ✅ Fixed Time Zone for All Students (Asia/Kolkata)
TIMEZONE = pytz.timezone("Asia/Kolkata")

# ✅ Function to get current local time in ISO 8601 format (with timezone)
def get_local_time():
    # Get current UTC time
    utc_now = datetime.now(pytz.utc)
    
    # Convert UTC time to local time (Asia/Kolkata)
    local_time = utc_now.astimezone(TIMEZONE)
    return local_time

# ✅ Student Data (Initial)
ourdata = [
    {
        "_id": "201022539002",
        "name": "Dasari Akhil",
        "group": "MSDS-3",
        "total_attendance": 0,
        "year": "2022-2025",
        "last_attendance_time": None,
        "attendance_time_log": []
    },
    {
        "_id": "201022539009",
        "name": "perry Rahul",
        "group": " MSDS-3",
        "total_attendance": 7,
        "year": "2022-2025",
        "last_attendance_time": None,
        "attendance_time_log": []
    },
    {
        "_id": "201022539001",
        "name": "Bonepalli Lokesh",
        "group": "MSDS-3",
        "total_attendance": 7,
        "year": "2022-2025",
        "last_attendance_time": None,
        "attendance_time_log": []
    },
    {
        "_id": "201022539008",
        "name": "Asad",
        "group": "MSDS-3",
        "total_attendance": 8,
        "year": "2022-2025",
        "last_attendance_time": None,
        "attendance_time_log": []
    },
    {
        "_id": "201022539004",
        "name": "Giri suraj",
        "group": "MSDS-3",
        "total_attendance": 0,
        "year": "2022-2025",
        "last_attendance_time": None,
        "attendance_time_log": []
    }
    
]

# 🔄 Insert/Update Data in MongoDB
for student in ourdata:
    collection.update_one({"_id": student["_id"]}, {"$set": student}, upsert=True)

print("✅ Student data inserted/updated successfully.")

# 📌 Function to Mark Attendance (With ISO 8601 Format)
def mark_attendance(student_id):
    student = collection.find_one({"_id": student_id})

    if student:
        # Get current UTC time and convert it to local time
        current_time = get_local_time()
        
        # Convert the local time to ISO 8601 format for storage
        current_time_iso = current_time.isoformat()  # ISO 8601 format

        # Get last attendance time from database
        last_att_time_str = student.get('last_attendance_time', None)

        if last_att_time_str:
            try:
                # Parse last attendance time stored in ISO 8601 format
                last_att_time = datetime.fromisoformat(last_att_time_str)

                current_time_obj = get_local_time()
                time_diff = (current_time_obj - last_att_time).total_seconds()

                if time_diff < 60:
                    print(f"⏳ Too soon! {student['name']}'s last attendance: {last_att_time_str}")
                    return
            except Exception as e:
                print(f"⚠️ Error processing {student['name']}'s attendance: {e}")
                last_att_time = None

        # Increase attendance count
        new_attendance_count = student["total_attendance"] + 1

        # Convert existing datetime objects in attendance_time_log to ISO 8601 format
        attendance_time_log = student.get("attendance_time_log", [])
        updated_log = []

        for entry in attendance_time_log:
            if isinstance(entry, datetime):
                updated_log.append(entry.isoformat())  # Convert to ISO format
            else:
                updated_log.append(entry)

        # Add the new attendance log entry (in ISO 8601 format)
        updated_log.append(current_time_iso)

        # Update MongoDB with the new attendance count and log
        collection.update_one(
            {"_id": student_id},
            {
                "$set": {
                    "total_attendance": new_attendance_count,
                    "last_attendance_time": current_time_iso  # Store in ISO format
                },
                "$push": {"attendance_time_log": current_time_iso}  # Store in ISO format
            }
        )

        # Print success message
        print(f"✅ Attendance marked for {student['name']} at {current_time_iso}")
    else:
        print(f"❌ Student with ID {student_id} not found!")


# Example: Mark attendance for a student
mark_attendance("201022539002")

# Example: Retrieve and display student data after attendance
vk_data = collection.find_one({"_id": "201022539004"})
print(vk_data)

# collection.delete_many({})
# print("deleted")


# ✅ Close MongoDB Connection
client.close()
