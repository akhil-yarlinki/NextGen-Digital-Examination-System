# 🎓 Online Quiz & Examination System

A modern **Online Quiz & Examination Platform** built with **Django**, designed for **students and teachers** with timed quizzes, manual grading, leaderboard ranking, analytics, and a premium dashboard UI.

---

## 🚀 Features

### 👨‍🎓 Student Features
- Student Registration & Login
- Attend quizzes assigned to their class
- Timer-based quiz attempts
- One-time quiz attempt restriction
- View personal quiz results
- Track scores and performance
- Leaderboard ranking system
- Profile management

### 👨‍🏫 Teacher Features
- Teacher Login
- Create and manage quizzes
- Add MCQ, Short Answer, and Long Answer questions
- Review student submissions
- Manual grading for descriptive answers
- View student scores
- Track overall class performance

### ⚙️ System Features
- Role-based authentication (Student / Teacher / Admin)
- Timer with auto submission logic
- Marks system:
  - MCQ → 1 mark
  - Short Answer → 2 marks
  - Long Answer → 5 marks
- Premium responsive UI
- Leaderboard system
- Quiz attempt tracking
- Student profile & teacher profile
- Admin panel support

---

## 🛠️ Tech Stack

- **Backend:** Django, Python
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite3
- **Authentication:** Django Auth System
- **Icons:** Font Awesome

---

## 📂 Project Structure

```bash
online_quiz/
│
├── quiz/
│   ├── migrations/
│   ├── templates/
│   │   └── quiz/
│   ├── static/
│   │   └── css/
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── forms.py
│
├── online_quiz/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── db.sqlite3
├── manage.py
└── README.md

Open:
http://127.0.0.1:8000
Admin
http://127.0.0.1:8000/admin
