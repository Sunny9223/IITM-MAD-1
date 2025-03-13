from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from functools import wraps
from flask import session, redirect, url_for
import jsonify
from flask import jsonify
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from functools import wraps
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt
from controllers.init_db import init_db

app = Flask(__name__)
app.secret_key = 'random_secret_key'  # Change this to a random secret key

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in

# User class
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[2])
    return None
# Database setup

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']  # This will be the email
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob = request.form['dob']
        password = request.form['password']
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (username, full_name, qualification, dob, password, role) VALUES (?, ?, ?, ?, ?, ?)", 
                           (username, full_name, qualification, dob, hashed_password, 'user'))  # Default role is 'user'
            conn.commit()
            flash("Registration successful! You can now log in.", "success")  # Success message
            return redirect(url_for('login'))  # Redirect to login after successful registration
        except sqlite3.IntegrityError:
            flash("Username already exists. Please choose a different one.", "danger")  # Error message
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, role FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):  # Compare hashed password
            user_obj = User(user[0], user[1], user[3])
            login_user(user_obj)  # Log the user in
            flash("Login successful! Welcome back.", "success")  # Success message
            # Redirect based on user role
            if user[3] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash("Invalid credentials. Please try again.", "danger")  # Error message

    return render_template('login.html')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return redirect(url_for('home'))  # Redirect to home if not admin
        return f(*args, **kwargs)
    return decorated_function

# @app.route('/admin-dashboard')
# def admin_dashboard():
#     if 'username' in session and session['role'] == 'admin':
#         return render_template('admin_dashboard.html', username=session['username'])
#     return redirect(url_for('home'))

@app.route('/user-dashboard')
@login_required
def user_dashboard():
    if current_user.role == 'user':
        # Fetch available quizzes
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes")
        quizzes = cursor.fetchall()

        # Fetch user's previous quiz attempts
        cursor.execute("""
            SELECT 
                s.quiz_id, 
                s.total_scored, 
                s.time_stamp_of_attempt, 
                c.name, 
                sub.name,
                q.quiz_name,
                s.total_questions
            FROM 
                scores s
            JOIN 
                quizzes q ON s.quiz_id = q.id
            JOIN 
                chapters c ON q.chapter_id = c.id
            JOIN 
                subjects sub ON c.subject_id = sub.id
            WHERE 
                s.user_id = (SELECT id FROM users WHERE username = ?)
        """, (current_user.username,))
        previous_attempts = cursor.fetchall()
        conn.close()

        return render_template('user_dashboard.html', quizzes=quizzes, previous_attempts=previous_attempts)
    return redirect(url_for('home'))

@app.route('/attempt-quiz/<int:quiz_id>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    if 'username' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Process the quiz answers
        score = 0
        total_questions = 0
        print("request.form", request.form)

        # Connect to the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Fetch quiz questions
        cursor.execute("SELECT id, correct_option FROM questions WHERE quiz_id = ?", (quiz_id,))
        questions = cursor.fetchall()

        # Loop through the submitted answers
        for question in questions:
            question_id = question[0]
            correct_option = question[1]
            user_answer = request.form.get(f'question_{question_id}')  # Get the user's answer
            total_questions = request.form.get(f'total_questions')  # Get the total questions
            # Check if the answer is correct
            if user_answer and int(user_answer) == correct_option:
                score += 1  # Increment score if the answer is correct
        print("Loop completed", session['username'])
        # Record the score
        cursor.execute("INSERT INTO scores (quiz_id, user_id, time_stamp_of_attempt, total_scored, total_questions) VALUES (?, (SELECT id FROM users WHERE username = ?), datetime('now'), ?, ?)", 
                       (quiz_id, session['username'], score, total_questions))
        conn.commit()
        conn.close()

        # Flash the score message
        flash(f'Your score is {score} out of {total_questions}.', 'success')
        return redirect(url_for('user_dashboard'))  # Redirect to user dashboard after submission

    # Fetch quiz questions for GET request
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, question_statement, option1, option2, option3, option4 FROM questions WHERE quiz_id = ?", (quiz_id,))
    questions = cursor.fetchall()

    # Fetch the total duration for the quiz
    cursor.execute("SELECT time_duration FROM quizzes WHERE id = ?", (quiz_id,))
    total_duration = cursor.fetchone()[0]  # Get the total duration in minutes
    total_duration *= 60  # Convert to seconds

    conn.close()

    return render_template('attempt_quiz.html', quiz_id=quiz_id, questions=questions, total_duration=total_duration)

@app.route('/user/scores')
def user_scores():
    if 'username' not in session:
        return redirect(url_for('home'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT quiz_id, total_scored, time_stamp_of_attempt FROM scores WHERE user_id = (SELECT id FROM users WHERE username = ?)", (session['username'],))
    scores = cursor.fetchall()
    conn.close()

    return render_template('user_scores.html', scores=scores)

@app.route('/admin/subject', methods=['GET', 'POST'])
@admin_required
def subject():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Check if the subject already exists
        cursor.execute("SELECT * FROM subjects WHERE name=?", (name,))
        existing_subject = cursor.fetchone()

        if existing_subject:
            flash("Subject already exists. Please choose a different name.", "danger")  # Error message
            conn.close()
            return redirect(url_for('subject'))  # Redirect to the same page

        cursor.execute("INSERT INTO subjects (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        conn.close()
        
        flash("Subject added successfully!", "success")
        return redirect(url_for('subject'))  # Redirect to admin dashboard after creation

    else:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()
        conn.close()
        
        return render_template('subject.html', subjects=subjects)

@app.route('/admin/edit-subject/<int:subject_id>', methods=['GET', 'POST'])
@admin_required
def edit_subject(subject_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cursor.execute("UPDATE subjects SET name=?, description=? WHERE id=?", (name, description, subject_id))
        conn.commit()
        conn.close()
        
        flash("Subject updated successfully!", "success")
        return redirect(url_for('subject'))  # Redirect to the subjects route

    # Fetch the specific subject to edit
    cursor.execute("SELECT * FROM subjects WHERE id=?", (subject_id,))
    subject = cursor.fetchone()  # Fetch the single subject
    conn.close()
    
    return render_template('edit_subject.html', subject=subject)

@app.route('/admin/delete-subject/<int:subject_id>', methods=['POST', 'GET'])
# @admin_required
def delete_subject(subject_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
    conn.commit()
    conn.close()
    
    flash("Subject deleted successfully!", "success")
    return redirect(url_for('subject'))

@app.route('/admin/chapter', methods=['GET', 'POST'])
@admin_required
def chapter():
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        name = request.form['name']
        description = request.form['description']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Check if the chapter already exists for the selected subject
        cursor.execute("SELECT * FROM chapters WHERE name=? AND subject_id=?", (name, subject_id))
        existing_chapter = cursor.fetchone()

        if existing_chapter:
            flash("Chapter already exists under this subject. Please choose a different name.", "danger")  # Error message
            conn.close()
            return redirect(url_for('chapter'))  # Redirect to the same page

        cursor.execute("INSERT INTO chapters (subject_id, name, description) VALUES (?, ?, ?)", 
                       (subject_id, name, description))
        conn.commit()
        conn.close()
        
        flash("Chapter added successfully!", "success")
        return redirect(url_for('chapter'))  # Redirect to the chapters route

    # Fetch subjects to populate the dropdown
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    conn.close()

    # Fetch all chapters to display
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT subjects.name AS subject_name, chapters.id AS chapter_id, chapters.name AS chapter_name, chapters.description 
        FROM chapters
        JOIN subjects ON chapters.subject_id = subjects.id;
    ''')
    chapters = cursor.fetchall()
    conn.close()

    return render_template('chapter.html', subjects=subjects, chapters=chapters)  # Render the form for creating a chapter

@app.route('/admin/edit-chapter/<int:chapter_id>', methods=['GET', 'POST'])
@admin_required
def edit_chapter(chapter_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        subject_id = request.form['subject_id']  # Get the selected subject ID from the form
        name = request.form['name']
        description = request.form['description']
        
        # Update the chapter with the new values
        cursor.execute("UPDATE chapters SET subject_id=?, name=?, description=? WHERE id=?", (subject_id, name, description, chapter_id))
        conn.commit()
        conn.close()
        
        flash("Chapter updated successfully!", "success")
        return redirect(url_for('chapter'))  # Redirect to the chapters route

    # Fetch the specific chapter to edit
    cursor.execute("SELECT * FROM chapters WHERE id=?", (chapter_id,))
    chapter = cursor.fetchone()

    # Fetch all subjects to populate the dropdown
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    conn.close()
    
    return render_template('edit_chapter.html', chapter=chapter, subjects=subjects)

@app.route('/admin/delete-chapter/<int:chapter_id>', methods=['POST'])
@admin_required
def delete_chapter(chapter_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chapters WHERE id=?", (chapter_id,))
    conn.commit()
    conn.close()
    
    flash("Chapter deleted successfully!", "success")
    return redirect(url_for('chapter'))  # Redirect to the chapters route

@app.route('/fetch_subjects', methods=['GET'])
def fetch_subjects():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM subjects")
    subjects = cursor.fetchall()
    conn.close()
    return (subjects)

@app.route('/fetch_chapters/<int:subject_id>', methods=['GET'])
def fetch_chapters(subject_id):  # Corrected function name
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM chapters WHERE subject_id=?", (subject_id,))
    chapters = cursor.fetchall()
    conn.close()
    return (chapters)

@app.route('/admin/quiz', methods=['GET', 'POST'])
@admin_required
def create_quiz():
    if request.method == 'POST':
        # Check if a subject is selected
        if request.form.get('quiz_add') is not None:
            chapter_id = request.form['chapter_name']  # Get the chapter ID from the form
            quiz_name = request.form['quiz_name']  # Get the quiz name from the form
            date_of_quiz = request.form['date_of_quiz']
            time_duration_hours = int(request.form['time_duration_hours'])  # Get hours
            time_duration_minutes = int(request.form['time_duration_minutes'])  # Get minutes
            remarks = request.form.get('remarks', '')  # Default to empty if not provided
            
            # Check if the quiz already exists for the selected chapter
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quizzes WHERE quiz_name=? AND chapter_id=?", (quiz_name, chapter_id))
            existing_quiz = cursor.fetchone()

            if existing_quiz:
                flash("Quiz already exists under this chapter. Please choose a different name.", "danger")  # Error message
                conn.close()
                return redirect(url_for('create_quiz'))  # Redirect to the same page

            # Calculate total time duration in minutes
            total_time_duration = (time_duration_hours * 60) + time_duration_minutes
            
            # Insert the quiz data into the quizzes table
            cursor.execute('''
                INSERT INTO quizzes (chapter_id, quiz_name, date_of_quiz, time_duration, remarks)
                VALUES (?, ?, ?, ?, ?)
            ''', (chapter_id, quiz_name, date_of_quiz, total_time_duration, remarks))

            # Commit the changes and close the connection
            conn.commit()
            conn.close()

            # Flash a success message and redirect
            flash("Quiz created successfully!", "success")
            return redirect(url_for('create_quiz'))

    else:
        # Handle GET request to display the form
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM subjects")
        subjects = cursor.fetchall()

        cursor.execute("SELECT id, subject_id, name FROM chapters")
        chapters = cursor.fetchall()

        cursor.execute("SELECT * FROM quizzes")
        quizzes = cursor.fetchall()
        conn.close()
        return render_template('quiz.html', subjects=subjects, chapters=chapters, quizzes=quizzes)

@app.route('/admin/delete-quiz/<int:quiz_id>', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quizzes WHERE id=?", (quiz_id,))
    conn.commit()
    conn.close()
    
    flash("Quiz deleted successfully!", "success")
    return redirect(url_for('create_quiz'))

@app.route('/admin/edit-quiz/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def edit_quiz(quiz_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        print("Quiz is being updated, POST")
        quiz_name = request.form['quiz_name']  # Get the quiz name from the form
        date_of_quiz = request.form['date_of_quiz']
        time_duration_hours = int(request.form['time_duration_hours'])  # Get hours
        time_duration_minutes = int(request.form['time_duration_minutes'])  # Get minutes
        remarks = request.form['remarks']
        
        # Calculate total duration in minutes
        total_duration = (time_duration_hours * 60) + time_duration_minutes
        
        # Update the quiz with the new values
        cursor.execute("UPDATE quizzes SET quiz_name=?, date_of_quiz=?, time_duration=?, remarks=? WHERE id=?", 
                       (quiz_name, date_of_quiz, total_duration, remarks, quiz_id))
        conn.commit()
        conn.close()
        
        flash("Quiz updated successfully!", "success")
        return redirect(url_for('create_quiz'))  # Redirect to the quizzes list

    # Fetch the specific quiz to edit
    cursor.execute("SELECT * FROM quizzes WHERE id=?", (quiz_id,))
    quiz = cursor.fetchone()  # Fetch the quiz data to edit

    conn.close()
    
    return render_template('edit_quiz.html', quiz=quiz)  # Pass the quiz data to the template


@app.route('/quiz/select-chapter/<int:subject_id>', methods=['GET'])
def get_chapters(subject_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM chapters WHERE subject_id=?", (subject_id,))
    chapters = cursor.fetchall()
    conn.close()
    
    return render_template('select_chapter.html', chapters=chapters)


@app.route('/admin/question', methods=['GET', 'POST'])
@admin_required
def question():
    if request.method == 'POST':
        quiz_id = request.form['quiz_id']
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form.get('option3')  # Optional
        option4 = request.form.get('option4')  # Optional
        correct_option = request.form['correct_option']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO questions (quiz_id, question_statement, option1, option2, option3, option4, correct_option)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (quiz_id, question_statement, option1, option2, option3, option4, correct_option))
        conn.commit()
        conn.close()
        
        flash("Question added successfully!", "success")
        return redirect(url_for('question'))

    # Fetch quizzes to populate the dropdown
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT 
        subjects.name AS subject_name,
        chapters.name AS chapter_name,
        quizzes.id AS quiz_id,
        quizzes.quiz_name,
        quizzes.date_of_quiz,
        quizzes.time_duration,
        quizzes.remarks 
        
    FROM 
        quizzes
    JOIN 
        chapters ON quizzes.chapter_id = chapters.id
    JOIN 
        subjects ON chapters.subject_id = subjects.id;""")
    quizzes = cursor.fetchall()
    conn.close()
    print(quizzes)
    return render_template('question.html', quizzes=quizzes)  # Render the form for adding a question

@app.route('/admin/question_add', methods=['GET', 'POST'])
@admin_required
def question_add():
    # if request.method == 'POST':
    #     quiz_id = request.form['quiz_id']
    #     # Here you would handle the logic to add a question to the quiz
    #     # For example, you might want to redirect to a page where you can add questions
    #     flash("Question added successfully!", "success")
    #     return redirect(url_for('some_other_route'))  # Replace with the appropriate route

    # If it's a GET request, you can fetch the quiz details if needed
    quiz_id = request.args.get('quiz_id')
    quiz_subject = request.args.get('quiz_subject')
    quiz_chapter = request.args.get('quiz_chapter')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions where quiz_id = ?", (quiz_id,))
    questions = cursor.fetchall()
    conn.close()

    # Fetch quiz details or any other necessary data here
    return render_template('add_question.html', quiz_id=quiz_id, questions=questions, quiz_subject=quiz_subject, quiz_chapter=quiz_chapter)

@app.route('/admin/delete-question/<int:question_id>', methods=['POST'])
@admin_required
def delete_question(question_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id=?", (question_id,))
    conn.commit()
    conn.close()
    
    flash("Quiz deleted successfully!", "success")
    return redirect(url_for('question'))

@app.route('/admin/edit-question/<int:question_id>', methods=['GET', 'POST'])
@admin_required  # Ensure you have an admin_required decorator defined
def edit_question(question_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form.get('option3')  # Optional
        option4 = request.form.get('option4')  # Optional
        correct_option = request.form['correct_option']
        
        # Update the question in the database
        conn.execute('''
            UPDATE questions
            SET question_statement = ?, option1 = ?, option2 = ?, option3 = ?, option4 = ?, correct_option = ?
            WHERE id = ?
        ''', (question_statement, option1, option2, option3, option4, correct_option, question_id))
        
        conn.commit()
        conn.close()
        
        flash("Question updated successfully!", "success")
        return redirect(url_for('question'))  # Redirect to the questions route

    # Fetch the specific question to edit
    cursor.execute("SELECT * FROM questions WHERE id=?", (question_id,))
    question = cursor.fetchone()
    conn.close()
    
    if question is None:
        flash("Question not found!", "danger")
        return redirect(url_for('question'))  # Redirect if question not found

    return render_template('edit_question.html', question=question)

@app.route('/admin/manage-users', methods=['GET', 'POST'])
@admin_required
def manage_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        # Handle user deletion if a delete request is made
        user_id = request.form.get('delete_user_id')
        if user_id:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            flash("User deleted successfully!", "success")

    # Fetch all users
    cursor.execute("SELECT id, username, full_name, qualification FROM users where role = 'user'")
    users = cursor.fetchall()
    conn.close()

    return render_template('manage_users.html', users=users)

@app.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        role = request.form['role']
        update_password = request.form.get('update_password')  # Check if the checkbox is checked

        # Update the user in the database
        cursor.execute("UPDATE users SET username=?, full_name=?, qualification=?, role=? WHERE id=?", 
                       (username, full_name, qualification, role, user_id))

        # If the password update checkbox is checked, update the password
        if update_password:
            password = request.form['password']
            # Hash the password before storing (you should use a hashing library like bcrypt)
            cursor.execute("UPDATE users SET password=? WHERE id=?", (password, user_id))

        conn.commit()
        conn.close()

        flash("User updated successfully!", "success")
        return redirect(url_for('manage_users'))

    # Fetch the user to edit
    cursor.execute("SELECT id, username, full_name, qualification, role FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    return render_template('edit_user.html', user=user)

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Example queries to get data for charts
    cursor.execute("SELECT * FROM chapters")
    chapters = cursor.fetchall()
    total_chapters = len(chapters)  # Count of chapters

    # Fetch all questions
    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()
    total_questions = len(questions)  # Count of questions

    # Fetch all quizzes
    cursor.execute("SELECT * FROM quizzes")
    quizzes = cursor.fetchall()
    total_quizzes = len(quizzes)  # Count of quizzes

    # Fetch all scores
    cursor.execute("SELECT * FROM scores")
    scores = cursor.fetchall()
    total_scores = len(scores)  # Count of scores

    # Fetch all users with role 'user'
    cursor.execute("SELECT * FROM users WHERE role = 'user'")
    users = cursor.fetchall()
    total_users = len(users)  # Count of users

    # Fetch all subjects
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    total_subjects = len(subjects)  # Count of subjects

    conn.close()

    return render_template('admin_dash.html', 
                           total_chapters=total_chapters, 
                           total_questions=total_questions, 
                           total_quizzes=total_quizzes, 
                           total_users=total_users, 
                           total_scores=total_scores, 
                           total_subjects=total_subjects,
                           chapters=chapters,
                           questions=questions,
                           quizzes=quizzes,
                           scores=scores,
                           users=users,
                           subjects=subjects)

@app.route('/admin/dashboard/data', methods=['GET'])
@admin_required
def dashboard_data():
    subject_id = request.args.get('subject_id')
    chapter_id = request.args.get('chapter_id')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Example query to get filtered data based on subject and chapter
    if subject_id and chapter_id:
        cursor.execute("SELECT COUNT(*) FROM quizzes WHERE chapter_id = ?", (chapter_id,))
    elif subject_id:
        cursor.execute("SELECT COUNT(*) FROM quizzes WHERE chapter_id IN (SELECT id FROM chapters WHERE subject_id = ?)", (subject_id,))
    else:
        cursor.execute("SELECT COUNT(*) FROM quizzes")

    total_quizzes = cursor.fetchone()[0]

    # Return data as JSON
    return jsonify(total_quizzes=total_quizzes)

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'], role=session['role'])
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log the user out
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    # insert_sample_data()
    app.run(host='0.0.0.0', port=80, debug=True)
    # app.run(debug=True)