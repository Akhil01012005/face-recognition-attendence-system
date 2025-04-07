import os
import pandas as pd
from pymongo import MongoClient
import openpyxl
from datetime import datetime

# MongoDB Connection
client = MongoClient("mongodb+srv://dasariakhil:201022539002@cluster0.lonxb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['LFDCAttendence']
collection = db['Datascience']

# Fetch attendance data
data = list(collection.find({}, { "name": 1, "_id": 1, "group": 1, "year": 1, "total_attendance": 1, "attendance_time_log": 1}))

# Convert MongoDB data to Pandas DataFrame
df = pd.DataFrame(data)

# Rename '_id' to 'Student ID' for better readability
df.rename(columns={'_id': 'Student ID', 'total_attendance': 'Total Attendance', 'attendance_time_log': 'Attendance Log'}, inplace=True)

# Ensure the correct column order
df = df[['name', 'Student ID', 'group', 'year', 'Total Attendance', 'Attendance Log']]

# Get current date in 'YYYY-MM-DD' format
current_date = datetime.now().strftime('%Y-%m-%d')

# Specify custom folder path (ensure folder exists)
folder_path = "C:\\Users\\Akhil Dasari\\OneDrive\\Desktop"

# Create file name with current date
file_path = f"{folder_path}Attendance_Report_{current_date}.xlsx"

# Save to Excel file
df.to_excel(file_path, index=True, engine="openpyxl")

print(f"✅ Attendance data saved successfully to {file_path}")
