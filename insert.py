import sqlite3
import bcrypt
# Script to add sample data to the database
def insert_test_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Insert sample users with password "Password"
    users = [
        ('user1@example.com', 'User One', 'Bachelor of Science', '1990-01-01', bcrypt.hashpw('Password'.encode('utf-8'), bcrypt.gensalt()), 'user'),
        ('user2@example.com', 'User Two', 'Bachelor of Arts', '1992-02-02', bcrypt.hashpw('Password'.encode('utf-8'), bcrypt.gensalt()), 'user'),
        ('user3@example.com', 'User Three', 'Master of Science', '1988-03-03', bcrypt.hashpw('Password'.encode('utf-8'), bcrypt.gensalt()), 'user')
    ]
    cursor.executemany("INSERT OR IGNORE INTO users (username, full_name, qualification, dob, password, role) VALUES (?, ?, ?, ?, ?, ?)", users)

    # Insert sample subjects
    subjects = [
        ('Mathematics', 'Study of numbers, shapes, and patterns.', None),
        ('Physics', 'Study of matter, energy, and the fundamental forces of nature.', None),
        ('Chemistry', 'Study of substances, their properties, and reactions.', None)
    ]
    cursor.executemany("INSERT INTO subjects (name, description, additional_fields) VALUES (?, ?, ?)", subjects)

    # Insert sample chapters
    chapters = [
        (1, 'Algebra', 'Study of mathematical symbols and rules for manipulating them.', None),
        (1, 'Geometry', 'Study of shapes, sizes, and properties of space.', None),
        (2, 'Classical Mechanics', 'Study of the motion of bodies under the influence of forces.', None)
    ]
    cursor.executemany("INSERT INTO chapters (subject_id, name, description, additional_fields) VALUES (?, ?, ?, ?)", chapters)

    # Insert sample quizzes
    quizzes = [
        ('Algebra Quiz 1', 1, '2025-03-20', 1, 'First quiz on Algebra concepts.'),
        ('Physics Quiz 1', 3, '2025-03-25', 1, 'First quiz on Classical Mechanics.')
    ]
    cursor.executemany("INSERT INTO quizzes (quiz_name, chapter_id, date_of_quiz, time_duration, remarks) VALUES (?, ?, ?, ?, ?)", quizzes)

    # Insert sample questions for Algebra Quiz
    algebra_questions = [
        (1, 'What is 2 + 2?', '3', '4', '5', '6', 2),
        (1, 'What is the square root of 16?', '2', '3', '4', '5', 3),
        (1, 'What is 5 * 6?', '30', '25', '35', '40', 1),
        (1, 'What is 12 / 4?', '2', '3', '4', '5', 2),
        (1, 'What is 7 - 3?', '4', '3', '5', '2', 1),
        (1, 'What is 9 + 10?', '19', '20', '21', '18', 1),
        (1, 'What is 15 % 4?', '3', '2', '1', '0', 1),
        (1, 'What is 8 * 7?', '54', '56', '58', '60', 2),
        (1, 'What is 3^3?', '6', '9', '27', '12', 3),
        (1, 'What is 10 - 4?', '6', '5', '7', '8', 1)
    ]
    cursor.executemany("INSERT INTO questions (quiz_id, question_statement, option1, option2, option3, option4, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?)", algebra_questions)

    # Insert sample questions for Physics Quiz
    physics_questions = [
        (2, 'What is Newton\'s first law?', 'An object in motion stays in motion', 'F=ma', 'Energy cannot be created', 'For every action, there is an equal reaction', 1),
        (2, 'What is the unit of force?', 'Joule', 'Newton', 'Watt', 'Pascal', 2),
        (2, 'What is the acceleration due to gravity?', '9.8 m/s²', '10 m/s²', '9.8 km/h²', '8.9 m/s²', 1),
        (2, 'What is the formula for kinetic energy?', '1/2 mv²', 'mv', 'mgh', '1/2 mgh', 1),
        (2, 'What is the speed of light?', '300,000 km/s', '150,000 km/s', '400,000 km/s', '500,000 km/s', 1),
        (2, 'What is the principle of conservation of energy?', 'Energy cannot be created or destroyed', 'Energy can be created', 'Energy is always lost', 'Energy is always gained', 1),
        (2, 'What is the formula for work?', 'Force x Distance', 'Mass x Acceleration', 'Energy x Time', 'Power x Time', 1),
        (2, 'What is the unit of power?', 'Joule', 'Watt', 'Newton', 'Pascal', 2),
        (2, 'What is the formula for potential energy?', 'mgh', '1/2 mv²', 'mv', 'F=ma', 1),
        (2, 'What is the law of universal gravitation?', 'F = G(m1*m2)/r²', 'F = ma', 'E = mc²', 'p = mv', 1)
    ]
    cursor.executemany("INSERT INTO questions (quiz_id, question_statement, option1, option2, option3, option4, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?)", physics_questions)

    conn.commit()
    conn.close()

# Call the function to insert test data
insert_test_data()