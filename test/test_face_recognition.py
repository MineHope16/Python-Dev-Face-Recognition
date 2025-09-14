#!/usr/bin/env python3
"""
Simple test script to verify that face recognition is working with existing student images
"""
import os
import sqlite3
from deepface import DeepFace
import warnings
warnings.filterwarnings('ignore')

def test_face_recognition():
    print("Testing Face Recognition System...")
    print("=" * 50)
    
    # Check database connection
    try:
        conn = sqlite3.connect('../studentss.db')  # Updated path to parent directory
        c = conn.cursor()
        c.execute("SELECT name, roll_number, image_folder FROM students")
        students = c.fetchall()
        print(f"Found {len(students)} registered students:")
        
        for student in students:
            name, roll_number, image_folder = student
            print(f"  - {name} (Roll: {roll_number}) - Folder: {image_folder}")
            
            # Check if image folder exists
            if os.path.exists(image_folder):
                images = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]
                print(f"    Images found: {len(images)}")
                
                if len(images) >= 2:
                    # Test face verification with the student's own images
                    img1_path = os.path.join(image_folder, images[0])
                    img2_path = os.path.join(image_folder, images[1])
                    
                    try:
                        result = DeepFace.verify(
                            img1_path=img1_path,
                            img2_path=img2_path,
                            model_name="Facenet",
                            distance_metric="cosine",
                            enforce_detection=False,
                            threshold=0.65
                        )
                        
                        print(f"    Self-verification result: {result['verified']} (distance: {result['distance']:.4f})")
                        
                    except Exception as e:
                        print(f"    Error during verification: {str(e)}")
                else:
                    print(f"    Not enough images for testing")
            else:
                print(f"    Image folder not found: {image_folder}")
            
            print()
        
        conn.close()
        print("Face recognition test completed!")
        
    except Exception as e:
        print(f"Database error: {str(e)}")

if __name__ == "__main__":
    test_face_recognition()