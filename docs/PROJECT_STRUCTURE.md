# Project Structure Guide

## 📁 Updated Project Organization

The Face Recognition Attendance System has been reorganized for better maintainability:

```
Face-Recognition-Project/
├── assets/                     # 🖼️ All image assets
│   ├── background.jpg
│   ├── register.png
│   ├── face-recognition-System-scaled-1.png
│   ├── attendanceimg.png
│   ├── exit-button-emergency-icon-3d-rendering-illustration-png.png
│   └── export.png
├── test/                       # 🧪 Test and debug scripts
│   ├── test_face_recognition.py
│   ├── test_improved_recognition.py
│   └── debug_recognition.py
├── known_faces/                # 👥 Student face images
│   ├── temp.jpg
│   ├── 1/ (Dattaram's images)
│   └── 2/ (Samta's images)
├── FRAS.py                     # 🎯 Main application
├── init_db.py                  # 🗄️ Database initialization
├── studentss.db               # 💾 SQLite database
├── requirements.txt            # 📋 Dependencies
├── CHANGELOG.md               # 📝 Change documentation
└── README.md                  # 📖 Project documentation
```

## 🚀 Running the Application

### Main Application

```bash
# From project root
python FRAS.py
```

### Running Tests

```bash
# From project root, run specific tests:
python test/test_face_recognition.py
python test/test_improved_recognition.py
python test/debug_recognition.py

# Or from test directory:
cd test
python test_face_recognition.py
```

## 🔧 Path Updates Made

### Asset Paths

All image assets now use the `assets/` prefix:

- `background.jpg` → `assets/background.jpg`
- `register.png` → `assets/register.png`
- And all other PNG files...

### Test Database Paths

Test files now use relative paths to access the database:

- `studentss.db` → `../studentss.db` (from test folder)

## ✅ Verification

All paths have been updated and tested:

- ✅ Main application loads assets correctly
- ✅ Test scripts can access database from test folder
- ✅ All image files moved to assets folder
- ✅ Clean project root directory

## 📋 Benefits of New Structure

1. **Better Organization**: Clear separation of assets, tests, and core files
2. **Easier Maintenance**: Assets grouped together for easy management
3. **Cleaner Root**: Main directory only contains essential files
4. **Test Isolation**: All test files contained in dedicated folder
5. **Scalability**: Structure supports future expansion
