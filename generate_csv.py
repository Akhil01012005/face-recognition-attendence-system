import csv
import os
from pymongo import MongoClient

client = MongoClient("mongodb+srv://dasariakhil:201022539002@cluster0.lonxb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['LFDCAttendence']
collection = db['Datascience']



def export_attendance_to_csv():
    # Fetch all student records from MongoDB
    students = collection.find({})
    
    # Define the CSV file path
    csv_file_path = "attendance.csv"

    # Open the CSV file in write mode
    with open(csv_file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        
        # Write the header row
        writer.writerow(["ID", "Name", "Group", "Year", "Total Attendance", "Last Attendance Time", "Attendance Log"])
        
        # Write each student's data
        for student in students:
            writer.writerow([
                student.get("_id", ""),
                student.get("name", ""),
                student.get("group", ""),
                student.get("year", ""),
                student.get("total_attendance", 0),
                student.get("last_attendance_time", ""),
                ", ".join(student.get("attendance_time_log", []))  # Convert list to string
            ])

    print(f"✅ Attendance data exported to {os.path.abspath(csv_file_path)}")

# Call this function when you want to generate the CSV file
export_attendance_to_csv()
