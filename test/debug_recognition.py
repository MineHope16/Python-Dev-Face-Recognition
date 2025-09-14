#!/usr/bin/env python3
"""
Debug script to test face recognition between students
"""
import os
import sqlite3
from deepface import DeepFace
import warnings
warnings.filterwarnings('ignore')

def test_cross_student_recognition():
    print("Testing Cross-Student Face Recognition...")
    print("=" * 60)
    
    # Check database connection
    conn = sqlite3.connect('../studentss.db')  # Updated path to parent directory
    c = conn.cursor()
    c.execute("SELECT name, roll_number, image_folder FROM students")
    students = c.fetchall()
    conn.close()
    
    print(f"Found {len(students)} students:")
    for student in students:
        name, roll_number, image_folder = student
        print(f"  - {name} (Roll: {roll_number})")
    
    print("\nTesting cross-recognition between students...")
    print("=" * 60)
    
    # Test each student against every other student's images
    for i, student1 in enumerate(students):
        name1, roll1, folder1 = student1
        
        for j, student2 in enumerate(students):
            name2, roll2, folder2 = student2
            
            if i != j:  # Don't test student against themselves
                print(f"\nTesting: {name1} images vs {name2} images")
                print("-" * 40)
                
                # Get first image from each student
                if os.path.exists(folder1) and os.path.exists(folder2):
                    images1 = [f for f in os.listdir(folder1) if f.endswith('.jpg')]
                    images2 = [f for f in os.listdir(folder2) if f.endswith('.jpg')]
                    
                    if images1 and images2:
                        img1_path = os.path.join(folder1, images1[0])
                        img2_path = os.path.join(folder2, images2[0])
                        
                        try:
                            result = DeepFace.verify(
                                img1_path=img1_path,
                                img2_path=img2_path,
                                model_name="Facenet",
                                distance_metric="cosine",
                                enforce_detection=False,
                                threshold=0.65
                            )
                            
                            status = "✅ MATCH" if result['verified'] else "❌ NO MATCH"
                            print(f"  {status} - Distance: {result['distance']:.4f} (threshold: 0.65)")
                            
                            # If there's a false positive (different people matching)
                            if result['verified']:
                                print(f"  ⚠️  WARNING: {name1} is being matched as {name2}!")
                                print(f"      This could cause login issues!")
                        
                        except Exception as e:
                            print(f"  ❌ Error: {str(e)}")
    
    print(f"\n" + "=" * 60)
    print("Cross-recognition test completed!")
    
    # Now test with temp.jpg if it exists
    temp_path = '../known_faces/temp.jpg'  # Updated path to parent directory
    if os.path.exists(temp_path):
        print(f"\nTesting temp.jpg against all students...")
        print("=" * 40)
        
        for student in students:
            name, roll_number, image_folder = student
            if os.path.exists(image_folder):
                images = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]
                if images:
                    img_path = os.path.join(image_folder, images[0])
                    try:
                        result = DeepFace.verify(
                            img1_path=temp_path,
                            img2_path=img_path,
                            model_name="Facenet",
                            distance_metric="cosine",
                            enforce_detection=False,
                            threshold=0.65
                        )
                        
                        status = "✅ MATCH" if result['verified'] else "❌ NO MATCH"
                        print(f"  temp.jpg vs {name}: {status} - Distance: {result['distance']:.4f}")
                        
                    except Exception as e:
                        print(f"  temp.jpg vs {name}: Error - {str(e)}")

if __name__ == "__main__":
    test_cross_student_recognition()