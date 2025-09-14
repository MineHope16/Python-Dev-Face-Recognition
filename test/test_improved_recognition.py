#!/usr/bin/env python3
"""
Test the improved face recognition logic with strict thresholds
"""
import os
import sqlite3
from deepface import DeepFace
import warnings
warnings.filterwarnings('ignore')

def test_improved_recognition():
    print("Testing Improved Face Recognition Logic...")
    print("=" * 60)
    
    # Test with the new strict parameters
    conn = sqlite3.connect('../studentss.db')  # Updated path to parent directory
    c = conn.cursor()
    c.execute("SELECT name, roll_number, image_folder FROM students")
    students = c.fetchall()
    conn.close()
    
    # Test each student against their own images (should match)
    for student in students:
        name, roll_number, image_folder = student
        print(f"\nTesting {name} self-recognition:")
        print("-" * 40)
        
        if os.path.exists(image_folder):
            images = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]
            if len(images) >= 2:
                matches = 0
                distances = []
                
                # Test first image against all others
                base_img = os.path.join(image_folder, images[0])
                
                for i in range(1, len(images)):
                    test_img = os.path.join(image_folder, images[i])
                    
                    try:
                        result = DeepFace.verify(
                            img1_path=base_img,
                            img2_path=test_img,
                            model_name="Facenet",
                            distance_metric="cosine",
                            enforce_detection=False,
                            threshold=0.45
                        )
                        
                        distance = result.get('distance', 1.0)
                        distances.append(distance)
                        
                        if result['verified']:
                            matches += 1
                        
                        print(f"  Image {i}: Distance = {distance:.4f}, Match = {result['verified']}")
                        
                    except Exception as e:
                        print(f"  Image {i}: Error - {str(e)}")
                
                avg_distance = sum(distances) / len(distances) if distances else 1.0
                print(f"  Summary: {matches}/{len(images)-1} matches, avg distance: {avg_distance:.4f}")
                print(f"  Would be recognized: {matches >= 2 and avg_distance < 0.4}")
    
    # Test cross-student recognition (should NOT match)
    print(f"\n" + "=" * 60)
    print("Testing cross-student recognition (should NOT match):")
    
    if len(students) >= 2:
        student1 = students[0]
        student2 = students[1]
        
        name1, roll1, folder1 = student1
        name2, roll2, folder2 = student2
        
        print(f"\nTesting {name1} vs {name2}:")
        print("-" * 40)
        
        if os.path.exists(folder1) and os.path.exists(folder2):
            images1 = [f for f in os.listdir(folder1) if f.endswith('.jpg')]
            images2 = [f for f in os.listdir(folder2) if f.endswith('.jpg')]
            
            if images1 and images2:
                matches = 0
                distances = []
                
                # Test several combinations
                for i in range(min(3, len(images1))):
                    for j in range(min(3, len(images2))):
                        img1_path = os.path.join(folder1, images1[i])
                        img2_path = os.path.join(folder2, images2[j])
                        
                        try:
                            result = DeepFace.verify(
                                img1_path=img1_path,
                                img2_path=img2_path,
                                model_name="Facenet",
                                distance_metric="cosine",
                                enforce_detection=False,
                                threshold=0.45
                            )
                            
                            distance = result.get('distance', 1.0)
                            distances.append(distance)
                            
                            if result['verified']:
                                matches += 1
                            
                            print(f"  {name1}[{i}] vs {name2}[{j}]: Distance = {distance:.4f}, Match = {result['verified']}")
                            
                        except Exception as e:
                            print(f"  Error: {str(e)}")
                
                avg_distance = sum(distances) / len(distances) if distances else 1.0
                print(f"  Summary: {matches} matches out of {len(distances)} comparisons")
                print(f"  Average distance: {avg_distance:.4f}")
                print(f"  Would be confused: {matches >= 2 and avg_distance < 0.4}")

if __name__ == "__main__":
    test_improved_recognition()