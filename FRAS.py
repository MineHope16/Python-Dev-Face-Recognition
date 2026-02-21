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

# Setup the database
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

    # Create admin table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Reset admin credentials every time (delete and recreate)
    c.execute("DELETE FROM admin WHERE username = 'admin'")
    c.execute("INSERT INTO admin (username, password) VALUES ('admin', 'admin123')")
    print("Default admin reset: admin / admin123") 

    conn.commit()
    conn.close()


# Admin login function
def admin_login():
    setup_database()
    
    # Dark theme colors
    bg = "#1a1a2a"
    frame_bg = "#16213e"
    accent = "#e94560"
    white = "#ffffff"
    gray = "#888888"
    
    def verify_login():
        username = username_entry.get()
        password = password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Input Error", "Please enter both username and password")
            return
        
        conn = sqlite3.connect('studentss.db')
        c = conn.cursor()
        c.execute("DELETE FROM admin WHERE username = 'admin'")
        c.execute("INSERT INTO admin (username, password) VALUES ('admin', 'admin123')")
        conn.commit()
        c.execute("SELECT * FROM admin WHERE username = ? AND password = ?", (username, password))
        result = c.fetchone()
        conn.close()
        
        if result:
            login_window.destroy()
            main()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
    
    login_window = tk.Tk()
    login_window.title("Admin Login")
    login_window.state('zoomed')

    # Load background image
    try:
        bg_image = Image.open("assets/background.jpg")
        sw = login_window.winfo_screenwidth()
        sh = login_window.winfo_screenheight()
        bg_image = bg_image.resize((sw, sh), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        
        bg_label = tk.Label(login_window, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        login_window.configure(bg=bg)
    
    container = tk.Frame(login_window, bg=bg)
    container.pack(fill="both", expand=True, padx=30, pady=25)
    
    tk.Label(container, text="Admin Login", font=("Helvetica", 24, "bold"), 
            bg=bg, fg=accent).pack(pady=(15, 10))
    
    tk.Label(container, text="Username", font=("Helvetica", 11, "bold"), 
            bg=bg, fg=white).pack(anchor="w", pady=(10, 3))
    
    username_entry = tk.Entry(container, font=("Helvetica", 12), bg=frame_bg, fg=white,
                            bd=0, insertbackground=white, width=22)
    username_entry.pack(ipady=6)
    username_entry.focus()
    
    tk.Label(container, text="Password", font=("Helvetica", 11, "bold"), 
            bg=bg, fg=white).pack(anchor="w", pady=(15, 3))
    
    password_entry = tk.Entry(container, show="*", font=("Helvetica", 12), bg=frame_bg, fg=white,
                            bd=0, insertbackground=white, width=22)
    password_entry.pack(ipady=6)
    password_entry.bind("<Return>", lambda e: verify_login())
    
    tk.Button(container, text="LOGIN", command=verify_login,
             font=("Helvetica", 12, "bold"), bg=accent, fg=white,
             bd=0, width=18, cursor="hand2").pack(pady=(25, 8))
    
    tk.Button(container, text="Cancel", command=login_window.quit,
             font=("Helvetica", 10), bg=frame_bg, fg=gray,
             bd=0, width=12, cursor="hand2").pack(pady=(5, 10))
    
    tk.Label(container, text="Default: admin / admin123",
            font=("Helvetica", 8), bg=bg, fg=gray).pack(pady=(15, 0))
    
    # Change Password Button
    def open_change_password():
        change_window = tk.Toplevel(login_window)
        change_window.title("Change Password")
        change_window.geometry("400x350")
        change_window.configure(bg=bg)
        
        pw, ph = 400, 350
        sw, sh = change_window.winfo_screenwidth(), change_window.winfo_screenheight()
        x, y = (sw - pw)//2, (sh - ph)//2
        change_window.geometry(f"{pw}x{ph}+{x}+{y}")
        
        container = tk.Frame(change_window, bg=bg)
        container.pack(fill="both", expand=True, padx=30, pady=25)
        
        tk.Label(container, text="Change Password", font=("Helvetica", 18, "bold"), 
                bg=bg, fg=accent).pack(pady=(10, 20))
        
        tk.Label(container, text="Current Password", font=("Helvetica", 10, "bold"), 
                bg=bg, fg=white).pack(anchor="w", pady=(10, 3))
        
        current_pass = tk.Entry(container, show="*", font=("Helvetica", 12), bg=frame_bg, fg=white,
                                bd=0, insertbackground=white, width=22)
        current_pass.pack(ipady=6)
        current_pass.focus()
        
        tk.Label(container, text="New Password", font=("Helvetica", 10, "bold"), 
                bg=bg, fg=white).pack(anchor="w", pady=(15, 3))
        
        new_pass = tk.Entry(container, show="*", font=("Helvetica", 12), bg=frame_bg, fg=white,
                            bd=0, insertbackground=white, width=22)
        new_pass.pack(ipady=6)
        
        tk.Label(container, text="Confirm New Password", font=("Helvetica", 10, "bold"), 
                bg=bg, fg=white).pack(anchor="w", pady=(15, 3))
        
        confirm_pass = tk.Entry(container, show="*", font=("Helvetica", 12), bg=frame_bg, fg=white,
                               bd=0, insertbackground=white, width=22)
        confirm_pass.pack(ipady=6)
        
        def save_password():
            curr = current_pass.get()
            new = new_pass.get()
            conf = confirm_pass.get()
            
            if not curr or not new or not conf:
                messagebox.showerror("Input Error", "All fields are required")
                return
            
            if len(new) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters")
                return
            
            if new != conf:
                messagebox.showerror("Error", "New passwords do not match")
                return
            
            conn = sqlite3.connect('studentss.db')
            c = conn.cursor()
            c.execute("DELETE FROM admin WHERE username = 'admin'")
            c.execute("INSERT INTO admin (username, password) VALUES ('admin', 'admin123')")
            conn.commit()
            c.execute("SELECT password FROM admin WHERE username = 'admin'")
            stored = c.fetchone()
            
            if stored and stored[0] == curr:
                c.execute("UPDATE admin SET password = ? WHERE username = 'admin'", (new,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Password changed successfully!")
                change_window.destroy()
            else:
                conn.close()
                messagebox.showerror("Error", "Current password is incorrect")
        
        tk.Button(container, text="Save New Password", command=save_password,
                 font=("Helvetica", 11, "bold"), bg=accent, fg=white,
                 bd=0, width=18, cursor="hand2").pack(pady=(25, 10))
        
        tk.Button(container, text="Cancel", command=change_window.destroy,
                 font=("Helvetica", 10), bg=frame_bg, fg=gray,
                 bd=0, width=12, cursor="hand2").pack(pady=(5, 10))
    
    tk.Button(container, text="Change Password", command=open_change_password,
             font=("Helvetica", 9), bg=frame_bg, fg=white,
             bd=0, width=15, cursor="hand2").pack(pady=(10, 0))
    
    login_window.mainloop()


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


# Function to edit student details
def edit_student(root):
    # First, ask for roll number
    roll_number = simpledialog.askstring("Edit Student", "Enter Roll Number of the student to edit:")
    
    if roll_number is None:
        messagebox.showinfo("Cancelled", "Edit operation was cancelled.")
        return
    
    if not roll_number:
        messagebox.showwarning("Input Error", "Roll Number is required.")
        return

    if not roll_number.isdigit():
        messagebox.showerror("Input Error", "Roll Number must be an integer.")
        return

    roll_number = int(roll_number)

    # Check if student exists
    conn = sqlite3.connect('studentss.db')
    c = conn.cursor()
    c.execute("SELECT name, department, address, image_folder FROM students WHERE roll_number = ?", (roll_number,))
    student = c.fetchone()
    conn.close()

    if not student:
        messagebox.showerror("Not Found", f"No student found with Roll Number {roll_number}")
        return

    current_name, current_department, current_address, image_folder = student

    # Create edit form window
    form_window = tk.Toplevel(root)
    form_window.title("Edit Student Details")
    form_window.geometry("450x400")
    form_window.config(bg="#E3F2FD")

    # Function to move focus between fields when 'Enter' is pressed
    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"

    # Close window gracefully
    def on_close():
        messagebox.showinfo("Cancelled", "Student edit was cancelled.")
        form_window.destroy()

    form_window.protocol("WM_DELETE_WINDOW", on_close)

    # Stylish Label and Entry Design
    label_style = {'font': ('Arial', 12), 'bg': "#E3F2FD", 'fg': '#1E88E5', 'padx': 10, 'pady': 10}
    entry_style = {'width': 30, 'font': ('Arial', 12), 'bd': 3, 'fg': '#1565C0'}

    # Adding Text Instructions at the top
    instruction_label = tk.Label(form_window, text=f"Editing: {current_name} (Roll: {roll_number})", 
                                font=('Arial', 14), bg="#E3F2FD", fg="#1E88E5")
    instruction_label.grid(row=0, column=0, columnspan=2, pady=20)

    # Labels and Entries for Student Name, Department, and Address (with current values)
    tk.Label(form_window, text="Student Name:", **label_style).grid(row=1, column=0, sticky='w', padx=20, pady=10)
    name_entry = tk.Entry(form_window, **entry_style)
    name_entry.insert(0, current_name)  # Pre-fill with current value
    name_entry.grid(row=1, column=1, pady=10)
    name_entry.bind("<Return>", focus_next_widget)

    tk.Label(form_window, text="Department:", **label_style).grid(row=2, column=0, sticky='w', padx=20, pady=10)
    department_entry = tk.Entry(form_window, **entry_style)
    department_entry.insert(0, current_department)  # Pre-fill with current value
    department_entry.grid(row=2, column=1, pady=10)
    department_entry.bind("<Return>", focus_next_widget)

    tk.Label(form_window, text="Address:", **label_style).grid(row=3, column=0, sticky='w', padx=20, pady=10)
    address_entry = tk.Entry(form_window, **entry_style)
    address_entry.insert(0, current_address)  # Pre-fill with current value
    address_entry.grid(row=3, column=1, pady=10)
    address_entry.bind("<Return>", focus_next_widget)

    # Button styling
    button_style = {'font': ('Arial', 12, 'bold'), 'bg': '#1E88E5', 'fg': 'white', 'width': 20, 'relief': 'raised'}

    # Submit function to save changes
    def save_details():
        new_name = name_entry.get()
        new_department = department_entry.get()
        new_address = address_entry.get()

        if not new_name or not new_department or not new_address:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            conn = sqlite3.connect('studentss.db')
            c = conn.cursor()
            c.execute("UPDATE students SET name = ?, department = ?, address = ? WHERE roll_number = ?",
                      (new_name, new_department, new_address, roll_number))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success! 🎉", 
                               f"Student details updated successfully!\n\n"
                               f"Name: {new_name}\n"
                               f"Department: {new_department}\n"
                               f"Address: {new_address}\n\n"
                               f"Roll Number: {roll_number} (unchanged)")
            form_window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update student: {str(e)}")

    # Submit button
    save_button = tk.Button(form_window, text="💾 Save Changes", command=save_details, **button_style)
    save_button.grid(row=4, column=0, columnspan=2, pady=40)

    # Cancel button
    cancel_button = tk.Button(form_window, text="❌ Cancel", command=on_close,
                             font=('Arial', 12), bg="#e60000", fg="white", width=20, relief="raised")
    cancel_button.grid(row=5, column=0, columnspan=2, pady=10)



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

    # Get student name for notification
    conn = sqlite3.connect('studentss.db')
    c = conn.cursor()
    c.execute("SELECT name FROM students WHERE roll_number = ?", (roll_number,))
    student_record = c.fetchone()
    conn.close()

    student_name = student_record[0] if student_record else f"Roll Number {roll_number}"

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
    
    # Create the main window - adjusted size to fit all buttons perfectly
    root = tk.Tk()
    root.title("Face Recognition Attendance System")
    root.geometry("1200x700")
   

    
    # Load the background image
    try:
        bg_image = Image.open("assets/background.jpg")
        bg_image = bg_image.resize((1200, 700), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
    except FileNotFoundError:
        print("Error: Background image file not found.")
        return

    # Create a Label widget to display the background image
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Add a text label on top of the background image
    title_label = tk.Label(
        root,
        text="Face Recognition Attendance System",
        font=("Arial", 28, "bold"),
        fg="white",
        bg="#0073e6",
        padx=10,
        pady=10
    )
    title_label.place(x=450, y=30)


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

    # Button width and spacing - single row with 6 buttons
    btn_width = 160
    btn_height = 160
    label_height = 40
    frame_width = btn_width + 15
    gap = 15
    cols = 6
    rows = 1
    
    # Calculate total width and height for grid
    total_width = (frame_width * cols) + (gap * (cols - 1))
    total_height = btn_height + label_height + 25
    
    # Adjust window size to fit all buttons in one row
    window_width = total_width + 40
    window_height = total_height + 150
    root.geometry(f"{window_width}x{window_height}")
    
    # Reload background image with new size
    bg_image = Image.open("assets/background.jpg")
    bg_image = bg_image.resize((window_width, window_height), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label.configure(image=bg_photo)
    bg_label.image = bg_photo
    
    # Recenter title
    title_label.place(x=(window_width - 450) // 2, y=20)
    
    start_x = (window_width - total_width) // 2  # Center horizontally
    start_y = 90  # Fixed start position below title

    # All 6 buttons in single row
    
    # 1. Register
    student_frame = tk.Frame(root, bg="#cce6ff", bd=5, relief="ridge")
    student_frame.place(x=start_x, y=start_y, width=frame_width, height=total_height)
    b1 = tk.Button(student_frame, image=photo_img, cursor="hand2", borderwidth=0, command=lambda: add_new_student(root))
    b1.place(x=5, y=5, width=btn_width, height=btn_height)
    b1_label = tk.Button(student_frame, text="Register", font=("Arial", 11, "bold"), command=lambda: add_new_student(root), cursor="hand2", bg="#0073e6", fg="white", borderwidth=0)
    b1_label.place(x=5, y=btn_height+8, width=btn_width, height=label_height)

    # 2. Edit Student
    edit_frame = tk.Frame(root, bg="#cce6ff", bd=5, relief="ridge")
    edit_frame.place(x=start_x + (frame_width + gap)*1, y=start_y, width=frame_width, height=total_height)
    edit_photo = ImageTk.PhotoImage(Image.open("assets/register.png").resize((btn_width, btn_height), Image.Resampling.LANCZOS))
    b_edit = tk.Button(edit_frame, image=edit_photo, cursor="hand2", borderwidth=0, command=lambda: edit_student(root))
    b_edit.place(x=5, y=5, width=btn_width, height=btn_height)
    b_edit_label = tk.Button(edit_frame, text="Edit Student", font=("Arial", 11, "bold"), command=lambda: edit_student(root), cursor="hand2", bg="#0073e6", fg="white", borderwidth=0)
    b_edit_label.place(x=5, y=btn_height+8, width=btn_width, height=label_height)

    # 3. Mark Attendance
    register_frame = tk.Frame(root, bg="#cce6ff", bd=5, relief="ridge")
    register_frame.place(x=start_x + (frame_width + gap)*2, y=start_y, width=frame_width, height=total_height)
    b2 = tk.Button(register_frame, image=photo_img1, cursor="hand2", command=recognize_face, borderwidth=0)
    b2.place(x=5, y=5, width=btn_width, height=btn_height)
    b2_label = tk.Button(register_frame, text="Mark Attendance", font=("Arial", 11, "bold"), command=recognize_face, cursor="hand2", bg="#0073e6", fg="white", borderwidth=0)
    b2_label.place(x=5, y=btn_height+8, width=btn_width, height=label_height)

    # 4. Check Attendance
    recognition_frame = tk.Frame(root, bg="#cce6ff", bd=5, relief="ridge")
    recognition_frame.place(x=start_x + (frame_width + gap)*3, y=start_y, width=frame_width, height=total_height)
    b3 = tk.Button(recognition_frame, image=photo_img2, cursor="hand2", command=check_attendance, borderwidth=0)
    b3.place(x=5, y=5, width=btn_width, height=btn_height)
    b3_label = tk.Button(recognition_frame, text="Check Attendance", font=("Arial", 11, "bold"), command=check_attendance, cursor="hand2", bg="#0073e6", fg="white", borderwidth=0)
    b3_label.place(x=5, y=btn_height+8, width=btn_width, height=label_height)

    # 5. Export Attendance
    export_frame = tk.Frame(root, bg="#cce6ff", bd=5, relief="ridge")
    export_frame.place(x=start_x + (frame_width + gap)*4, y=start_y, width=frame_width, height=total_height)
    export_button = tk.Button(export_frame, image=photo_ex, cursor="hand2", borderwidth=0, command=generate_student_info_pdf)
    export_button.place(x=5, y=5, width=btn_width, height=btn_height)
    export_label = tk.Button(export_frame, text="Export", font=("Arial", 11, "bold"), command=generate_student_info_pdf, cursor="hand2", bg="#0073e6", fg="white", borderwidth=0)
    export_label.place(x=5, y=btn_height+8, width=btn_width, height=label_height)

    # 6. Exit
    exit_frame = tk.Frame(root, bg="#ffcccc", bd=5, relief="ridge")
    exit_frame.place(x=start_x + (frame_width + gap)*5, y=start_y, width=frame_width, height=total_height)
    b4 = tk.Button(exit_frame, image=photo_img3, cursor="hand2", borderwidth=0, command=root.quit)
    b4.place(x=5, y=5, width=btn_width, height=btn_height)
    b4_label = tk.Button(exit_frame, text="Exit", font=("Arial", 11, "bold"), cursor="hand2", bg="#e60000", fg="white", borderwidth=0, command=root.quit)
    b4_label.place(x=5, y=btn_height+8, width=btn_width, height=label_height)


    # Run the application
    root.mainloop()

# Student Login function
def student_login():
    bg = "#0f0c29"
    frame_bg = "#302b63"
    accent = "#00d4ff"
    white = "#ffffff"
    gray = "#888888"
    
    login_window = tk.Tk()
    login_window.title("Student Login")
    login_window.geometry("400x420")
    login_window.configure(bg=bg)
    login_window.resizable(False, False)
    
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    x = (screen_width - 400) // 2
    y = (screen_height - 420) // 2
    login_window.geometry(f"400x420+{x}+{y}")
    
    container = tk.Frame(login_window, bg=bg)
    container.pack(fill="both", expand=True, padx=30, pady=30)
    
    tk.Label(container, text="Student Login", font=("Helvetica", 22, "bold"), bg=bg, fg=accent).pack(pady=(10, 5))
    tk.Label(container, text="Face Recognition Attendance", font=("Helvetica", 9), bg=bg, fg=gray).pack(pady=(0, 20))
    
    tk.Label(container, text="Roll Number", font=("Helvetica", 10, "bold"), bg=bg, fg=white).pack(anchor="w", pady=(10, 5))
    
    roll_entry = tk.Entry(container, font=("Helvetica", 11), bg=frame_bg, fg=white, bd=0, insertbackground=white, width=20)
    roll_entry.pack(ipady=5)
    roll_entry.focus()
    
    tk.Label(container, text="Use face recognition for attendance", font=("Helvetica", 8), bg=bg, fg=gray).pack(pady=(5, 15))
    
    def verify_student():
        roll_number = roll_entry.get()
        
        if not roll_number:
            messagebox.showerror("Input Error", "Please enter your Roll Number")
            return
        
        if not roll_number.isdigit():
            messagebox.showerror("Input Error", "Roll Number must be an integer")
            return
        
        roll_number = int(roll_number)
        
        conn = sqlite3.connect('studentss.db')
        c = conn.cursor()
        c.execute("SELECT name, roll_number FROM students WHERE roll_number = ?", (roll_number,))
        student = c.fetchone()
        conn.close()
        
        if student:
            name, roll = student
            login_window.destroy()
            student_main(name, roll)
        else:
            messagebox.showerror("Not Found", "Roll Number not found. Contact admin to register.")
    
    tk.Button(container, text="LOGIN", command=verify_student, font=("Helvetica", 11, "bold"), bg=accent, fg="#0f0c29", bd=0, width=18, cursor="hand2").pack(pady=(15, 10))
    
    tk.Button(container, text="Back to Main Menu", command=lambda: [login_window.destroy(), main_menu_select()], font=("Helvetica", 10), bg=frame_bg, fg=gray, bd=0, width=18, cursor="hand2").pack(pady=(5, 0))
    
    login_window.mainloop()


# Student Main Menu
def student_main(student_name, roll_number):
    # Create student window
    root = tk.Tk()
    root.title(f"Welcome {student_name}!")
    root.geometry("800x600")
    root.config(bg="#E3F2FD")
    
    # Center the window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 800) // 2
    y = (screen_height - 600) // 2
    root.geometry(f"800x600+{x}+{y}")
    
    # Header
    header_frame = tk.Frame(root, bg="#0073e6", pady=20)
    header_frame.pack(fill="x")
    
    welcome_label = tk.Label(header_frame, text=f"🎓 Welcome, {student_name}!", 
                            font=("Arial", 24, "bold"), bg="#0073e6", fg="white")
    welcome_label.pack()
    
    roll_label = tk.Label(header_frame, text=f"Roll Number: {roll_number}", 
                         font=("Arial", 14), bg="#0073e6", fg="white")
    roll_label.pack()
    
    # Buttons Frame
    btn_frame = tk.Frame(root, bg="#E3F2FD", pady=50)
    btn_frame.pack(expand=True)
    
    # Mark Attendance Button
    def student_mark_attendance():
        root.destroy()
        recognize_for_student(student_name, roll_number)
    
    mark_btn = tk.Button(btn_frame, text="📸 Mark My Attendance", command=student_mark_attendance,
                        font=("Arial", 16, "bold"), bg="#28a745", fg="white",
                        width=25, height=2, relief="raised")
    mark_btn.pack(pady=20)
    
    # View My Attendance Button
    def view_my_attendance():
        conn = sqlite3.connect('studentss.db')
        c = conn.cursor()
        c.execute("SELECT login_time, logout_time FROM attendance WHERE roll_number = ? ORDER BY login_time DESC", (roll_number,))
        records = c.fetchall()
        conn.close()
        
        if records:
            total = len(records)
            info = f"📊 Your Attendance Report\n\n"
            info += f"Total Sessions: {total}\n\n"
            info += "Recent Sessions:\n"
            for i, (login, logout) in enumerate(records[:5]):
                info += f"{i+1}. Login: {login}"
                if logout:
                    info += f" | Logout: {logout}\n"
                else:
                    info += " | Still logged in\n"
            messagebox.showinfo("My Attendance", info)
        else:
            messagebox.showinfo("No Records", "No attendance records found.")
    
    view_btn = tk.Button(btn_frame, text="📋 View My Attendance", command=view_my_attendance,
                        font=("Arial", 16, "bold"), bg="#17a2b8", fg="white",
                        width=25, height=2, relief="raised")
    view_btn.pack(pady=20)
    
    # Retake Photos Button
    def retake_photos():
        # Warning message
        if not messagebox.askyesno("⚠️ Retake Photos", 
            "You are about to retake your photos.\n\n"
            "⚠️ WARNING: Your old photos will be DELETED and replaced with new ones.\n\n"
            "This may affect face recognition accuracy if the new photos are not clear.\n\n"
            "Do you want to continue?"):
            return
        
        # Get student's image folder
        conn = sqlite3.connect('studentss.db')
        c = conn.cursor()
        c.execute("SELECT image_folder FROM students WHERE roll_number = ?", (roll_number,))
        result = c.fetchone()
        conn.close()
        
        if not result:
            messagebox.showerror("Error", "Student record not found.")
            return
        
        image_folder = result[0]
        
        # Delete old photos
        if os.path.exists(image_folder):
            for file in os.listdir(image_folder):
                try:
                    os.remove(os.path.join(image_folder, file))
                except:
                    pass
        
        # Show instructions
        messagebox.showinfo("📸 Photo Capture", 
                           "We need to capture 5 new photos.\n\n"
                           "Please ensure:\n"
                           "• Good lighting on your face\n"
                           "• Look directly at the camera\n"
                           "• Remove sunglasses/hat if any\n\n"
                           "Get ready for Photo 1!")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Camera Error", "Cannot access camera.")
            return
        
        img_count = 0
        max_images = 5
        
        try:
            while img_count < max_images:
                current_photo = img_count + 1
                window_title = f"📸 Photo {current_photo}/{max_images}"
                
                captured = False
                while not captured:
                    ret, frame = cap.read()
                    if not ret:
                        messagebox.showerror("Error", "Failed to capture from camera.")
                        cap.release()
                        return
                    
                    # Add text on frame
                    cv2.putText(frame, f"Photo {current_photo}/{max_images}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "Press SPACE to capture", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.imshow(window_title, frame)
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == ord(' '):
                        image_path = os.path.join(image_folder, f"{roll_number}_{img_count}.jpg")
                        cv2.imwrite(image_path, frame)
                        
                        success_msg = f"✅ Photo {current_photo}/{max_images} captured!"
                        if current_photo < max_images:
                            success_msg += f"\n\nGet ready for Photo {current_photo + 1}!"
                        else:
                            success_msg += "\n\n🎉 All photos updated!"
                        
                        messagebox.showinfo("Photo Captured", success_msg)
                        captured = True
                        img_count += 1
                    
                    elif key == ord('q'):
                        if messagebox.askyesno("Cancel", "Cancel retaking photos?"):
                            cap.release()
                            cv2.destroyAllWindows()
                            return
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
        
        if img_count == max_images:
            messagebox.showinfo("✅ Success!", 
                              f"🎉 All 5 photos have been updated successfully!\n\n"
                              f"Your new photos are now saved in the system.\n\n"
                              f"Thank you!")
        else:
            messagebox.showwarning("Incomplete", f"Only {img_count} out of {max_images} photos were saved.")
    
    retake_btn = tk.Button(btn_frame, text="📸 Retake Photos", command=retake_photos,
                          font=("Arial", 16, "bold"), bg="#ff9800", fg="white",
                          width=25, height=2, relief="raised")
    retake_btn.pack(pady=20)
    
    # Logout Button
    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            root.destroy()
            main_menu_select()
    
    logout_btn = tk.Button(btn_frame, text="🚪 Logout", command=logout,
                          font=("Arial", 14), bg="#e60000", fg="white",
                          width=20, relief="raised")
    logout_btn.pack(pady=20)
    
    root.mainloop()


# Recognize face for student (simplified)
def recognize_for_student(student_name, roll_number):
    cap = cv2.VideoCapture(0)
    
    start_time = time.time()
    captured_image_path = 'known_faces/temp.jpg'

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture video.")
            cap.release()
            return
        
        cv2.putText(frame, "Look at the camera...", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Mark Attendance - Smile!", frame)

        if time.time() - start_time >= 3:
            cv2.imwrite(captured_image_path, frame)
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            student_main(student_name, roll_number)
            return

    cap.release()
    cv2.destroyAllWindows()

    try:
        # Get student's image folder
        conn = sqlite3.connect('studentss.db')
        c = conn.cursor()
        c.execute("SELECT image_folder FROM students WHERE roll_number = ?", (roll_number,))
        result = c.fetchone()
        
        if not result:
            messagebox.showerror("Error", "Student record not found.")
            student_main(student_name, roll_number)
            return
            
        image_folder = result[0]
        
        # Verify face
        matches = 0
        distances = []
        
        for img_file in os.listdir(image_folder):
            img_path = os.path.join(image_folder, img_file)
            try:
                verify_result = DeepFace.verify(
                    img1_path=captured_image_path,
                    img2_path=img_path,
                    model_name="Facenet",
                    distance_metric="cosine",
                    enforce_detection=False,
                    threshold=0.45
                )
                
                if verify_result.get('verified'):
                    matches += 1
                    distances.append(verify_result.get('distance', 1.0))
            except:
                continue
        
        conn.close()
        
        if os.path.exists(captured_image_path):
            os.remove(captured_image_path)
        if matches >= 1:
            # Mark attendance
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            conn = sqlite3.connect('studentss.db')
            c = conn.cursor()
            
            # Check if already logged in today
            c.execute("SELECT id, logout_time FROM attendance WHERE roll_number = ? AND DATE(login_time) = DATE('now')", (roll_number,))
            record = c.fetchone()
            
            if record and record[1] is None:
                c.execute("UPDATE attendance SET logout_time = ? WHERE id = ?", (current_time, record[0]))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Goodbye {student_name}! Logout time recorded.")
            elif record:
                messagebox.showinfo("Already Done", "You have already marked attendance today!")
            else:
                c.execute("INSERT INTO attendance (roll_number, login_time) VALUES (?, ?)", (roll_number, current_time))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Welcome {student_name}! Attendance marked successfully!")
            
            student_main(student_name, roll_number)
        else:
            messagebox.showerror("Failed", "Face not recognized. Please try again.")
            student_main(student_name, roll_number)
            
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        student_main(student_name, roll_number)


# Main Menu (Login Selection)
def main_menu_select():
    menu_window = tk.Tk()
    menu_window.title("Face Recognition Attendance System")
    menu_window.geometry("500x400")
    menu_window.config(bg="#E3F2FD")
    
    # Center the window
    screen_width = menu_window.winfo_screenwidth()
    screen_height = menu_window.winfo_screenheight()
    x = (screen_width - 500) // 2
    y = (screen_height - 400) // 2
    menu_window.geometry(f"500x400+{x}+{y}")
    
    # Title
    title_label = tk.Label(menu_window, text="🎯 Attendance System", 
                          font=("Arial", 28, "bold"), bg="#E3F2FD", fg="#1E88E5")
    title_label.pack(pady=40)
    
    # Admin Button
    admin_btn = tk.Button(menu_window, text="🔐 Admin Login", 
                        command=lambda: [menu_window.destroy(), admin_login()],
                        font=("Arial", 16, "bold"), bg="#1E88E5", fg="white",
                        width=20, height=2, relief="raised")
    admin_btn.pack(pady=20)
    
    # Student Button
    student_btn = tk.Button(menu_window, text="🎓 Student Login", 
                          command=lambda: [menu_window.destroy(), student_login()],
                          font=("Arial", 16, "bold"), bg="#28a745", fg="white",
                          width=20, height=2, relief="raised")
    student_btn.pack(pady=20)
    
    # Exit Button
    exit_btn = tk.Button(menu_window, text="❌ Exit", 
                        command=menu_window.quit,
                        font=("Arial", 12), bg="#e60000", fg="white",
                        width=15, relief="raised")
    exit_btn.pack(pady=20)
    
    menu_window.mainloop()


# Run the main function
if __name__ == "__main__":
    main_menu_select()
