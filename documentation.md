# Flask Quiz Application Documentation

## Overview
This Flask application is designed to manage a quiz system where users can register, log in, attempt quizzes, and view their scores. Administrators can manage users, subjects, chapters, quizzes, and questions. The application uses SQLite for data storage and bcrypt for password hashing.

## Table of Contents
1. [Installation](#installation)
2. [Application Structure](#application-structure)
3. [Database Schema](#database-schema)
4. [Routes](#routes)
5. [User Roles](#user-roles)
6. [Security](#security)
7. [Running the Application](#running-the-application)

## Installation
1. **Clone the repository**:
git clone github_repository

2. **Create a virtual environment**:
Run the following command to create a virtual environment (you can name it `venv` or any name you prefer):
python -m venv venv
Activate the virtual environment:
* On Windows: `venv\Scripts\activate`
* On macOS (used for developing project) and Linux: `source venv/bin/activate`
2. **Install dependencies**:
Ensure you have Python and pip installed, then run:
bash pip3 install Flask Flask-Login bcrypt 
OR
`pip3 install -r requirements.txt`

3. **Set up the database**:
   The application will automatically create the SQLite database (`database.db`) when it runs for the first time.

## Application Structure
The application consists of the following main components:
- **app.py**: The main application file containing all the routes and logic.
- **templates**: Directory containing HTML templates for rendering views.
- **static**: Directory for static files (CSS, JavaScript, images).

## Database Schema
The application uses the following tables in the SQLite database:

1. **users**: Stores user information.
   - `id`: Primary key.
   - `username`: Unique username (email).
   - `full_name`: User's full name.
   - `qualification`: User's qualification.
   - `dob`: Date of birth.
   - `password`: Hashed password.
   - `role`: User role (admin/user).

2. **subjects**: Stores subjects for quizzes.
   - `id`: Primary key.
   - `name`: Subject name.
   - `description`: Subject description.

3. **chapters**: Stores chapters under each subject.
   - `id`: Primary key.
   - `subject_id`: Foreign key referencing `subjects`.
   - `name`: Chapter name.
   - `description`: Chapter description.

4. **quizzes**: Stores quizzes related to chapters.
   - `id`: Primary key.
   - `quiz_name`: Name of the quiz.
   - `chapter_id`: Foreign key referencing `chapters`.
   - `date_of_quiz`: Date of the quiz.
   - `time_duration`: Duration of the quiz in minutes.
   - `remarks`: Additional remarks.

5. **questions**: Stores questions for each quiz.
   - `id`: Primary key.
   - `quiz_id`: Foreign key referencing `quizzes`.
   - `question_statement`: The question text.
   - `option1`, `option2`, `option3`, `option4`: Possible answers.
   - `correct_option`: Index of the correct answer.

6. **scores**: Stores scores for each quiz attempt.
   - `id`: Primary key.
   - `quiz_id`: Foreign key referencing `quizzes`.
   - `user_id`: Foreign key referencing `users`.
   - `time_stamp_of_attempt`: Timestamp of the attempt.
   - `total_scored`: Total score achieved.
   - `total_questions`: Total number of questions in the quiz.

## Routes

### User Routes
- **Home**: 
  - **Path**: `/`
  - **Method**: GET
  - **Description**: Renders the landing page.

- **User Registration**: 
  - **Path**: `/register`
  - **Methods**: GET, POST
  - **Description**: Handles user registration on GET request. On POST, it creates a new user.

- **User Login**: 
  - **Path**: `/login`
  - **Methods**: GET, POST
  - **Description**: Handles user login on GET request. On POST, it authenticates the user.

- **User Dashboard**: 
  - **Path**: `/user-dashboard`
  - **Method**: GET
  - **Description**: Displays available quizzes and previous attempts for logged-in users.

- **Attempt Quiz**: 
  - **Path**: `/attempt-quiz/<int:quiz_id>`
  - **Methods**: GET, POST
  - **Description**: Allows users to attempt a specific quiz on GET request. On POST, it processes the quiz answers.

- **User Scores**: 
  - **Path**: `/user/scores`
  - **Method**: GET
  - **Description**: Displays the scores of the logged-in user.

- **Logout**: 
  - **Path**: `/logout`
  - **Method**: GET
  - **Description**: Logs the user out and redirects to the home page.

### Admin Routes
- **Admin Dashboard**: 
  - **Path**: `/admin/dashboard`
  - **Method**: GET
  - **Description**: Displays statistics and management options for administrators.

- **Manage Users**: 
  - **Path**: `/admin/manage-users`
  - **Methods**: GET, POST
  - **Description**: Allows administrators to manage user accounts on GET request. On POST, it handles user deletion.

- **Subject Management**: 
  - **Path**: `/admin/subject`
  - **Methods**: GET, POST
  - **Description**: Allows administrators to add, edit, and delete subjects.

- **Chapter Management**: 
  - **Path**: `/admin/chapter`
  - **Methods**: GET, POST
  - **Description**: Allows administrators to add, edit, and delete chapters.

- **Quiz Management**: 
  - **Path**: `/admin/quiz`
  - **Methods**: GET, POST
  - **Description**: Allows administrators to create, edit, and delete quizzes.

- **Question Management**: 
  - **Path**: `/admin/question`
  - **Methods**: GET, POST
  - **Description**: Allows administrators to add, edit, and delete questions.

- **Edit User**: 
  - **Path**: `/admin/edit-user/<int:user_id>`
  - **Methods**: GET, POST
  - **Description**: Allows administrators to edit user details.

- **Delete User**: 
  - **Path**: `/admin/delete-user/<int:user_id>`
  - **Method**: POST
  - **Description**: Deletes a user account.

### Additional Routes
- **Fetch Subjects**: 
  - **Path**: `/fetch_subjects`
  - **Method**: GET
  - **Description**: Returns a list of subjects.

- **Fetch Chapters**: 
  - **Path**: `/fetch_chapters/<int:subject_id>`
  - **Method**: GET
  - **Description**: Returns a list of chapters for a specific subject.

- **Dashboard**: 
  - **Path**: `/dashboard`
  - **Method**: GET
  - **Description**: Displays the user dashboard if logged in.

## User Roles
The application supports two user roles:
- **Admin**: Has full access to manage users, subjects, chapters, quizzes, and questions.
- **User**: Can register, log in, attempt quizzes, and view their scores.

## Security
- Passwords are hashed using bcrypt before being stored in the database.
- Flask-Login is used to manage user sessions and authentication.
- Admin routes are protected with a custom decorator (`admin_required`) to ensure only admins can access them.

## Running the Application
To run the application, execute the following command in the terminal:

## Run python app.py

The application will start on `http://0.0.0.0:80` (or `http://localhost:80`).

## Conclusion
This documentation provides an overview of the Flask quiz application, including its structure, functionality, and usage. For further customization or development, refer to the code in `app.py` and the associated templates.