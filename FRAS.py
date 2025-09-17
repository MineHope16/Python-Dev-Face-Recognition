import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging
import cv2
import sqlite3
from tkinter import Tk, Button, Label, Entry, Toplevel, simpledialog, messagebox
from deepface import DeepFace
import warnings
warnings.filterwarnings('ignore')
import datetime
import time
import tkinter as tk
from PIL import Image, ImageTk
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import sqlite3
import os



# Setup the database if not already present
def setup_database():
    conn = sqlite3.connect('studentss.db')
    c = conn.cursor()
    
    # Create students table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number INTEGER UNIQUE NOT NULL,
            department TEXT NOT NULL,
            address TEXT NOT NULL,
            image_folder TEXT NOT NULL
        )
    ''')

    # Create attendance table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number INTEGER NOT NULL,
            login_time TEXT,
            logout_time TEXT,
            FOREIGN KEY (roll_number) REFERENCES students (roll_number)
        )
    ''')

    conn.commit()
    conn.close()


def add_new_student(root):
    form_window = tk.Toplevel(root)
    form_window.title("Enter Student Details")

    # Set window size and center it
    form_window.geometry("450x400")
  
    form_window.config(bg="#E3F2FD")

    # Function to move focus between fields when 'Enter' is pressed
    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"

    # Close window gracefully
    def on_close():
        messagebox.showinfo("Cancelled", "Student registration was cancelled.")
        form_window.destroy()

    form_window.protocol("WM_DELETE_WINDOW", on_close)

    # Stylish Label and Entry Design
    label_style = {'font': ('Arial', 12), 'bg': "#E3F2FD", 'fg': '#1E88E5', 'padx': 10, 'pady': 10}
    entry_style = {'width': 30, 'font': ('Arial', 12), 'bd': 3, 'fg': '#1565C0'}

    # Adding Text Instructions at the top
    instruction_label = tk.Label(form_window, text="Please enter the student details below:", font=('Arial', 14), bg="#E3F2FD", fg="#1E88E5")
    instruction_label.grid(row=0, column=0, columnspan=2, pady=20)

    # Labels and Entries for Student Name, Roll Number, Department, and Address
    tk.Label(form_window, text="Student Name:", **label_style).grid(row=1, column=0, sticky='w', padx=20, pady=10)
    name_entry = tk.Entry(form_window, **entry_style)
    name_entry.grid(row=1, column=1, pady=10)
    name_entry.bind("<Return>", focus_next_widget)

    tk.Label(form_window, text="Roll Number:", **label_style).grid(row=2, column=0, sticky='w', padx=20, pady=10)
    roll_number_entry = tk.Entry(form_window, **entry_style)
    roll_number_entry.grid(row=2, column=1, pady=10)
    roll_number_entry.bind("<Return>", focus_next_widget)

    tk.Label(form_window, text="Department:", **label_style).grid(row=3, column=0, sticky='w', padx=20, pady=10)
    department_entry = tk.Entry(form_window, **entry_style)
    department_entry.grid(row=3, column=1, pady=10)
    department_entry.bind("<Return>", focus_next_widget)

    tk.Label(form_window, text="Address:", **label_style).grid(row=4, column=0, sticky='w', padx=20, pady=10)
    address_entry = tk.Entry(form_window, **entry_style)
    address_entry.grid(row=4, column=1, pady=10)
    address_entry.bind("<Return>", focus_next_widget)

     # Button styling
    button_style = {'font': ('Arial', 12, 'bold'), 'bg': '#1E88E5', 'fg': 'white', 'width': 20, 'relief': 'raised'}

    # Submit function
    def submit_details():
        name = name_entry.get()
        roll_number = roll_number_entry.get()
        department = department_entry.get()
        address = address_entry.get()

        if not name or not roll_number or not department or not address:
            messagebox.showerror("Input Error", "All fields are required.")
            return
        if not roll_number.isdigit():
            messagebox.showerror("Input Error", "Roll Number must be an integer.")
            return

        roll_number = int(roll_number)
        
        # Check if the roll number already exists in the database
        conn = sqlite3.connect('studentss.db')
        c = conn.cursor()
        c.execute("SELECT roll_number FROM students WHERE roll_number = ?", (roll_number,))
        if c.fetchone():
            messagebox.showerror("Error", "A student with this Roll Number already exists.")
            conn.close()
            return
        conn.close()

        # Create image folder
        image_folder = os.path.join("known_faces", str(roll_number))
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        # Show initial message
        messagebox.showinfo("Photo Capture Process", 
                           "📸 For better face recognition accuracy, we need to capture 5 photos.\n\n"
                           "Please ensure:\n"
                           "• Good lighting on your face\n"
                           "• Look directly at the camera\n"
                           "• Remove sunglasses/hat if any\n\n"
                           "Each photo will be taken one by one with your permission.\n"
                           "Get ready for Photo 1!")

        cap = cv2.VideoCapture(0)  # Use default camera
        if not cap.isOpened():
            messagebox.showerror("Camera Error", "Cannot access camera. Please check camera connection.")
            return

        img_count = 0
        max_images = 5
        photos_captured = []

        try:
            while img_count < max_images:
                # Show current photo number
                current_photo = img_count + 1
                
                # Create a window for live preview
                window_title = f"📸 Photo {current_photo}/{max_images} - Press SPACE to Capture or Q to Cancel"
                
                captured = False
                while not captured:
                    ret, frame = cap.read()
                    if not ret:
                        messagebox.showerror("Error", "Failed to capture from camera.")
                        cap.release()
                        return

                    # Add instruction text on the frame
                    instruction_text = f"Photo {current_photo}/{max_images} - Press SPACE to capture"
                    cv2.putText(frame, instruction_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    ready_text = "Position yourself and press SPACE when ready"
                    cv2.putText(frame, ready_text, (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    cv2.imshow(window_title, frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    
                    # Capture photo on SPACE key
                    if key == ord(' '):  # Space bar
                        # Save the image
                        image_path = os.path.join(image_folder, f"{roll_number}_{img_count}.jpg")
                        cv2.imwrite(image_path, frame)
                        photos_captured.append(image_path)
                        
                        # Show success message
                        success_msg = f"✅ Photo {current_photo}/{max_images} captured successfully!"
                        if current_photo < max_images:
                            success_msg += f"\n\nGet ready for Photo {current_photo + 1}!"
                        else:
                            success_msg += "\n\n🎉 All photos captured! Processing registration..."
                        
                        messagebox.showinfo("Photo Captured", success_msg)
                        captured = True
                        img_count += 1
                        
                    # Cancel on Q key
                    elif key == ord('q'):
                        if messagebox.askyesno("Cancel Registration", 
                                             f"Are you sure you want to cancel registration?\n"
                                             f"You have captured {img_count} out of {max_images} photos."):
                            cap.release()
                            cv2.destroyAllWindows()
                            # Clean up partially captured images
                            for photo in photos_captured:
                                if os.path.exists(photo):
                                    os.remove(photo)
                            if os.path.exists(image_folder) and not os.listdir(image_folder):
                                os.rmdir(image_folder)
                            messagebox.showinfo("Cancelled", "Student registration was cancelled.")
                            form_window.destroy()
                            return

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during photo capture: {str(e)}")
            cap.release()
            cv2.destroyAllWindows()
            return
        
        finally:
            cap.release()
            cv2.destroyAllWindows()

        # If all photos were captured successfully
        if img_count == max_images:
            conn = sqlite3.connect('studentss.db')
            c = conn.cursor()
            c.execute("INSERT INTO students (name, roll_number, department, address, image_folder) VALUES (?, ?, ?, ?, ?)",
                      (name, roll_number, department, address, image_folder))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Registration Complete! 🎉", 
                               f"Congratulations {name}!\n\n"
                               f"✅ All 5 photos captured successfully\n"
                               f"✅ Student information saved\n"
                               f"✅ Roll Number: {roll_number}\n\n"
                               f"You can now use the Face Recognition feature for attendance.\n"
                               f"Thank you for your patience! 😊")
        else:
            messagebox.showinfo("Registration Incomplete", 
                               f"Registration was not completed.\n"
                               f"Only {img_count} out of {max_images} photos were captured.")

        form_window.destroy()

    # Submit button with unique style
    submit_button = tk.Button(form_window, text="📸 Register & Take Photos", command=submit_details, **button_style)
    submit_button.grid(row=5, column=0, columnspan=2, pady=40)


# Function to recognize a face and log login/logout times
def recognize_face():
    cap = cv2.VideoCapture(0)  # Use default camera
    
    start_time = time.time()
    recognized = False
    captured_image_path = 'known_faces/temp.jpg'

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture video.")
            cap.release()
            return
        
        cv2.imshow("Recognizing Face - Wait 2 seconds", frame)

        if time.time() - start_time >= 4:
            cv2.imwrite(captured_image_path, frame)
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            response = messagebox.askyesno("Stop Recognition", "You have stopped recognizing. Do you want to continue?")
            if not response:  # If the user chooses 'No'
                cap.release()
                cv2.destroyAllWindows()
                messagebox.showinfo("Cancelled", "Face recognition was stopped by the user.")
                return

    cap.release()
    cv2.destroyAllWindows()

    try:
        print(f"🚀 Starting face recognition process...")
        conn = sqlite3.connect('studentss.db')
        c = conn.cursor()
        c.execute("SELECT name, roll_number, image_folder FROM students")
        students = c.fetchall()
        print(f"👥 Found {len(students)} registered students in database")

        recognized = False
        best_match = None
        best_distance = float('inf')
        match_count = 0
        
        for student in students:
            name, roll_number, image_folder = student
            print(f"Attempting to recognize {name} (Roll: {roll_number})")
            
            if not os.path.exists(image_folder):
                print(f"Warning: Image folder not found for {name}: {image_folder}")
                continue
            
            student_matches = 0
            student_distances = []
            
            for img_file in os.listdir(image_folder):
                img_path = os.path.join(image_folder, img_file)
                print(f"Comparing with image: {img_path}")
                
                try:
                    result = DeepFace.verify(
                        img1_path=captured_image_path,
                        img2_path=img_path,
                        model_name="Facenet",
                        distance_metric="cosine",
                        enforce_detection=False,
                        threshold=0.45  # Made threshold much more strict
                    )
                    
                    distance = result.get('distance', 1.0)
                    student_distances.append(distance)
                    
                    print(f"Distance for {name}: {distance:.4f}")
                    
                    if result.get('verified'):
                        student_matches += 1
                        print(f"Match found with {name} (Match #{student_matches})")
                        
                except Exception as e:
                    print(f"Error processing {img_path}: {str(e)}")
                    continue
            
            # A student needs at least 2 matches out of their images to be considered
            if student_matches >= 2:
                avg_distance = sum(student_distances) / len(student_distances) if student_distances else 1.0
                print(f"{name}: {student_matches} matches, avg distance: {avg_distance:.4f}")
                
                if avg_distance < best_distance:
                    best_distance = avg_distance
                    best_match = (name, roll_number)
                    match_count += 1
        
        # Only proceed if we have exactly one strong match
        if match_count == 1 and best_match and best_distance < 0.4:
            name, roll_number = best_match
            print(f"🎯 STRONG MATCH FOUND! Student identified as {name} with confidence distance: {best_distance:.4f}")
            print(f"📝 Match count: {match_count}, Roll number: {roll_number}")
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"⏰ Current time: {current_time}")
            
            try:
                # Log attendance
                print(f"🔍 Checking existing attendance for roll number: {roll_number}")
                c.execute("SELECT id, login_time, logout_time FROM attendance WHERE roll_number = ? AND DATE(login_time) = DATE('now')", (roll_number,))
                record = c.fetchone()
                print(f"📋 Existing record found: {record}")
                
                if record:
                    if record[2] is None:  # No logout time
                        print(f"⚠️ Student already logged in today, asking for logout")
                        if messagebox.askyesno("Logout", f"{name} ({roll_number}) is already logged in today. Do you want to log out?"):
                            print(f"✅ User chose to logout, updating record ID: {record[0]}")
                            c.execute("UPDATE attendance SET logout_time = ? WHERE id = ?", (current_time, record[0]))
                            conn.commit()
                            print(f"💾 Logout record committed to database")
                            messagebox.showinfo("Logout", f"Goodbye {name}! Logout time recorded.")
                            return
                        else:
                            print(f"❌ User chose not to logout")
                            return
                    else:
                        print(f"ℹ️ Student already completed attendance for today")
                        messagebox.showinfo("Already Logged", f"{name} has already completed attendance for today.")
                        return
                else:
                    print(f"🆕 No existing record, creating new attendance entry")
                    print(f"📝 Executing INSERT: roll_number={roll_number}, login_time={current_time}")
                    c.execute("INSERT INTO attendance (roll_number, login_time) VALUES (?, ?)", (roll_number, current_time))
                    
                    # Verify the insert worked
                    print(f"💾 Committing transaction to database...")
                    conn.commit()
                    print(f"✅ Transaction committed successfully!")
                    
                    # Double-check the record was inserted
                    c.execute("SELECT * FROM attendance WHERE roll_number = ? AND login_time = ?", (roll_number, current_time))
                    verify_record = c.fetchone()
                    print(f"🔍 Verification - Record inserted: {verify_record}")
                    
                    messagebox.showinfo("Success", f"Welcome {name}! Attendance marked successfully!")
                    print(f"🎉 Attendance successfully recorded for {name}")
                    return
                    
            except Exception as db_error:
                print(f"❌ DATABASE ERROR during attendance recording: {str(db_error)}")
                print(f"🔧 Error type: {type(db_error).__name__}")
                messagebox.showerror("Database Error", f"Failed to record attendance: {str(db_error)}")
                return
        elif match_count > 1:
            print(f"⚠️ AMBIGUOUS RECOGNITION: {match_count} students matched - rejecting for security")
            messagebox.showwarning("Ambiguous Recognition", "Multiple students matched. Please ensure good lighting and try again.")
        else:
            print(f"❌ NO RECOGNITION: No students matched the face (match_count={match_count})")
            print(f"🔍 Best match was: {best_match} with distance: {best_distance:.4f}")
            messagebox.showwarning("Not Recognized", "No matching student found. Please try again or register if you're new.")
            
    except Exception as e:
        print(f"Error during face recognition: {str(e)}")
        messagebox.showerror("Error", "An error occurred during face recognition. Please try again.")
    finally:
        if os.path.exists(captured_image_path):
            os.remove(captured_image_path)
        conn.close()

def check_attendance():
    roll_number = simpledialog.askstring("Attendance Check", "Enter Roll Number:")
    
    if roll_number is None:
        # User cancelled the input dialog
        messagebox.showinfo("Cancelled", "Attendance check was cancelled.")
        return
    
    if not roll_number:
        messagebox.showwarning("Input Error", "Roll Number is required.")
        return

    if not roll_number.isdigit():
        messagebox.showerror("Input Error", "Roll Number must be an integer.")
        return

    roll_number = int(roll_number)

    conn = sqlite3.connect('studentss.db')
    c = conn.cursor()
    
    # Query to fetch all attendance records for the specified roll number
    c.execute("SELECT login_time, logout_time FROM attendance WHERE roll_number = ?", (roll_number,))
    attendance_records = c.fetchall()

    # Count total attendance and group by date
    total_attendance = len(attendance_records)
    date_records = {}

    for record in attendance_records:
        login_time, logout_time = record
        date = login_time.split(" ")[0]  # Get only the date part
        
        if date not in date_records:
            date_records[date] = []
        date_records[date].append((login_time, logout_time))

    conn.close()

    # Calculate attendance percentage out of 100 days
    total_days = 100  # Assuming we're tracking attendance over 100 days
    attendance_percentage = (total_attendance / total_days) * 100

    # Prepare the attendance summary message
    if total_attendance > 0:
        attendance_info = f"Total Attendance: {total_attendance} out of {total_days} days ({attendance_percentage:.2f}%)\n\n"
        for date, records in date_records.items():
            attendance_info += f"{date}:\n"
            for login_time, logout_time in records:
                attendance_info += f"  Login: {login_time}  Logout: {logout_time if logout_time else 'N/A'}\n"
        messagebox.showinfo("Attendance Records", f"Attendance for Roll Number {roll_number}:\n\n{attendance_info}")
    else:

        messagebox.showinfo("No Records", "No attendance records found for this Roll Number.")

def generate_student_info_pdf():
    conn = sqlite3.connect('studentss.db')
    c = conn.cursor()
    
    # Query to fetch all students' information
    c.execute("SELECT name, department, roll_number FROM students")
    students = c.fetchall()
    
    # Create a PDF document
    pdf_file = "attendance_report.pdf"
    document = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []
    
    # Add title
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.units import inch
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.darkblue
    )
    
    # Add title and date
    title = Paragraph("📊 Face Recognition Attendance System Report", title_style)
    elements.append(title)
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,  # Center alignment
        spaceAfter=20
    )
    
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    date_para = Paragraph(f"Generated on: {current_date}", date_style)
    elements.append(date_para)
    elements.append(Spacer(1, 20))
    
    # Process each student
    for student_index, student in enumerate(students):
        name, department, roll_number = student
        
        # Add student header
        student_style = ParagraphStyle(
            'StudentHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=10,
            textColor=colors.darkgreen
        )
        
        student_header = Paragraph(
            f"🎓 {name} (Roll: {roll_number}) - {department} Department", 
            student_style
        )
        elements.append(student_header)
        
        # Get all attendance records for this student
        c.execute("""
            SELECT login_time, logout_time 
            FROM attendance 
            WHERE roll_number = ? 
            ORDER BY login_time DESC
        """, (roll_number,))
        attendance_records = c.fetchall()
        
        if attendance_records:
            # Create table for this student's attendance
            attendance_data = [["📅 Date", "📆 Day", "🕐 Login Time", "🕐 Logout Time", "⏱️ Duration"]]
            
            total_duration_minutes = 0
            
            for login_time_str, logout_time_str in attendance_records:
                # Parse login time
                login_dt = datetime.strptime(login_time_str, "%Y-%m-%d %H:%M:%S")
                date_str = login_dt.strftime("%b %d, %Y")
                day_str = login_dt.strftime("%A")
                login_display = login_dt.strftime("%I:%M %p")
                
                # Parse logout time if available
                if logout_time_str:
                    logout_dt = datetime.strptime(logout_time_str, "%Y-%m-%d %H:%M:%S")
                    logout_display = logout_dt.strftime("%I:%M %p")
                    
                    # Calculate duration
                    duration = logout_dt - login_dt
                    duration_hours = duration.total_seconds() / 3600
                    total_duration_minutes += duration.total_seconds() / 60
                    
                    if duration_hours < 1:
                        duration_str = f"{int(duration.total_seconds() / 60)} min"
                    else:
                        hours = int(duration_hours)
                        minutes = int((duration_hours - hours) * 60)
                        duration_str = f"{hours}h {minutes}m"
                else:
                    logout_display = "Not logged out"
                    duration_str = "N/A"
                
                attendance_data.append([
                    date_str,
                    day_str,
                    login_display,
                    logout_display,
                    duration_str
                ])
            
            # Create table with attendance data
            attendance_table = Table(attendance_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            attendance_table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Data styling
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                
                # Special styling for incomplete sessions (no logout)
                ('TEXTCOLOR', (3, 1), (3, -1), colors.red),  # Logout time column
            ]))
            
            elements.append(attendance_table)
            
            # Add summary for this student
            total_days = len(attendance_records)
            total_hours = total_duration_minutes / 60 if total_duration_minutes > 0 else 0
            
            summary_style = ParagraphStyle(
                'Summary',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=20,
                leftIndent=20
            )
            
            summary_text = f"""
            📈 <b>Summary:</b> Total Attendance Days: {total_days} | 
            Total Hours: {total_hours:.1f}h | 
            Average per Day: {total_hours/total_days:.1f}h
            """
            
            summary_para = Paragraph(summary_text, summary_style)
            elements.append(summary_para)
            
        else:
            # No attendance records
            no_data_style = ParagraphStyle(
                'NoData',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=20,
                leftIndent=20,
                textColor=colors.red
            )
            no_data = Paragraph("❌ No attendance records found for this student.", no_data_style)
            elements.append(no_data)
        
        # Add separator between students (except for the last one)
        if student_index < len(students) - 1:
            elements.append(Spacer(1, 30))
    
    conn.close()
    
    # Build the PDF
    document.build(elements)
    
    messagebox.showinfo(
        "📊 Attendance Report Generated!",
        f"✅ Detailed attendance report has been successfully generated!\n\n"
        f"📄 File Name: attendance_report.pdf\n"
        f"📁 Location: {os.path.abspath(pdf_file)}\n\n"
        f"📋 Report includes:\n"
        f"• Date and day for each attendance\n"
        f"• Complete login/logout times\n"
        f"• Duration calculations\n"
        f"• Student-wise summaries\n\n"
        f"🚀 Opening report now..."
    )
    os.startfile(pdf_file)
    

def main():
    # Initialize database first
    setup_database()
    
    # Create the main window
    root = tk.Tk()
    root.title("Face Recognition Attendance System")
    root.geometry("1900x1050")  # Adjusted window size
   

    
    # Load the background image
    try:
        bg_image = Image.open("assets/background.jpg")  # Updated path to assets folder
        bg_image = bg_image.resize((1500, 1000), Image.Resampling.LANCZOS)  # Resize to fit the window
        bg_photo = ImageTk.PhotoImage(bg_image)
    except FileNotFoundError:
        print("Error: Background image file not found.")
        return

    # Create a Label widget to display the background image
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Cover the entire window

    # Add a text label on top of the background image
    title_label = tk.Label(
        root,
        text="Face Recognition Attendance System",
        font=("Arial", 35, "bold"),
        fg="white",
        bg="#0073e6",  # Background of the text label (can be transparent if you prefer)
        padx=10,
        pady=15
    )
    title_label.place(x=400, y=80)  # Position it at the top center


    # Load the image for the buttons    
    try:
        img = Image.open("assets/register.png")  
        img = img.resize((220, 220), Image.Resampling.LANCZOS)
        photo_img = ImageTk.PhotoImage(img)

        img_student = Image.open("assets/face-recognition-System-scaled-1.png") 
        img_student = img_student.resize((220, 220), Image.Resampling.LANCZOS)
        photo_img1 = ImageTk.PhotoImage(img_student)
        
        img_student1 = Image.open("assets/attendanceimg.png")  
        img_student1 = img_student1.resize((220, 220), Image.Resampling.LANCZOS)
        photo_img2 = ImageTk.PhotoImage(img_student1)

        img_student2 = Image.open("assets/exit-button-emergency-icon-3d-rendering-illustration-png.png") 
        img_student2 = img_student2.resize((220, 220), Image.Resampling.LANCZOS)
        photo_img3 = ImageTk.PhotoImage(img_student2)    
        
        img_ex = Image.open("assets/export.png")  
        img_ex = img_ex.resize((220, 220), Image.Resampling.LANCZOS)
        photo_ex = ImageTk.PhotoImage(img_ex)
    except FileNotFoundError:
        print("Error: Button image file not found.")
        return

    
    # Frame for "Register"
    student_frame = tk.Frame(root, bg="#cce6ff", bd=5, relief="ridge")
    student_frame.place(x=50, y=300, width=250, height=300)
    b1 = tk.Button(student_frame, image=photo_img, cursor="hand2", borderwidth=0,command=lambda: add_new_student(root),)
    b1.place(x=10, y=10, width=220, height=220)

    b1_label = tk.Button(student_frame, text="Register", font=("Arial", 14),command=lambda: add_new_student(root), cursor="hand2",
                         bg="#0073e6", fg="white", borderwidth=0)
    b1_label.place(x=10, y=240, width=220, height=40)

    # Frame for "Face Recognition"
    register_frame = tk.Frame(root, bg="#cce6ff", bd=5, relief="ridge")
    register_frame.place(x=350, y=300, width=250, height=300)

    b2 = tk.Button(register_frame, image=photo_img1, cursor="hand2",command=recognize_face, borderwidth=0)
    b2.place(x=10, y=10, width=220, height=220)

    b2_label = tk.Button(register_frame, text="Face Recognition", command=recognize_face,font=("Arial", 14), cursor="hand2",
                         bg="#0073e6", fg="white", borderwidth=0)
    b2_label.place(x=10, y=240, width=220, height=40)

    # Frame for "Check Attendance"
    recognition_frame = tk.Frame(root, bg="#cce6ff", bd=5, relief="ridge")
    recognition_frame.place(x=630, y=300, width=250, height=300)

    b3 = tk.Button(recognition_frame, image=photo_img2, cursor="hand2", command=check_attendance,borderwidth=0)
    b3.place(x=10, y=10, width=220, height=220)

    b3_label = tk.Button(recognition_frame, text="Check Attendance",command=check_attendance, font=("Arial", 14), cursor="hand2",
                         bg="#0073e6", fg="white", borderwidth=0)
    b3_label.place(x=10, y=240, width=220, height=40)

    # Frame for "Exit" with similar image style
    exit_frame = tk.Frame(root, bg="#cce6ff", bd=5, relief="ridge")
    exit_frame.place(x=1200, y=300, width=250, height=300)

    b4 = tk.Button(exit_frame, image=photo_img3, cursor="hand2", borderwidth=0, command=root.quit)
    b4.place(x=10, y=10, width=220, height=220)

    b4_label = tk.Button(exit_frame, text="Exit", font=("Arial", 14), cursor="hand2",
                         bg="#e60000", fg="white", borderwidth=0, command=root.quit)
    b4_label.place(x=10, y=240, width=220, height=40)
    # Frame for "Export Attendance"
    export_frame = tk.Frame(root, bg="#cce6ff", bd=5, relief="ridge")
    export_frame.place(x=900, y=300, width=250, height=300)

    export_button = tk.Button(export_frame, image=photo_ex, cursor="hand2", borderwidth=0, command=generate_student_info_pdf)
    export_button.place(x=10, y=10, width=220, height=220)

    export_label = tk.Button(export_frame, text="Export Attendance", font=("Arial", 14), command=generate_student_info_pdf, 
                         cursor="hand2", bg="#0073e6", fg="white", relief="raised")
    export_label.place(x=10, y=240, width=220, height=40)


    # Run the application
    root.mainloop()

# Run the main function
if __name__ == "__main__":
    main()
