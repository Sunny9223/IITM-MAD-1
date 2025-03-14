import sqlite3
import bcrypt

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,  -- This will be the email
            full_name TEXT,
            qualification TEXT,
            dob DATE,
            password TEXT,
            role TEXT
        )
    ''')
    admin_password = 'admin'  # Plain text password
    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())

    # Insert admin user with hashed password
    cursor.execute("INSERT OR IGNORE INTO users (username, full_name, qualification, dob, password, role) VALUES (?, ?, ?, ?, ?, ?)", 
                   ('admin', 'admin', 'admin', '10-09-2002', hashed_password, 'admin'))  # Change 'admin_password' to a secure password
 # Change 'admin_password' to a secure password

    
    # Create Subjects Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            additional_fields TEXT
        )
    ''')

    # Create Chapters Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            additional_fields TEXT,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')

    # Create Quizzes Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_name TEXT NOT NULL,
    chapter_id INTEGER NOT NULL,
    date_of_quiz DATE NOT NULL,
    time_duration INTEGER NOT NULL,  -- Change to INTEGER to store total minutes
    remarks TEXT,
    FOREIGN KEY (chapter_id) REFERENCES chapters (id) ON DELETE CASCADE
)
''')

    # Create Questions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            question_statement TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT,
            option4 TEXT,
            correct_option INTEGER, -- This will store the index of the correct option (1-4)
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
        )
    ''')

    # Create Scores Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            user_id INTEGER,
            time_stamp_of_attempt DATETIME,
            total_scored INTEGER,
            total_questions INTEGER,
            additional_fields TEXT,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    