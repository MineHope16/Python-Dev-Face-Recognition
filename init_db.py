import sqlite3

def init_database():
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
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()