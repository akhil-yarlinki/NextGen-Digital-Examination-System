from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('teacherlogin/', views.teacher_login_view, name='teacherlogin'),
    path('studentlogin/', views.student_login_view, name='studentlogin'),
    path('register/', views.register_view, name='register'),
    path('create-teacher/', views.create_teacher_account, name='create_teacher'),

    path('teacher-dashboard/', views.teacher_dashboard_view, name='teacher-dashboard'),
    path('student-dashboard/', views.student_dashboard_view, name='student-dashboard'),

    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('review-answers/', views.review_answers_view, name='review_answers'),
    path('grade-answer/<int:answer_id>/', views.grade_answer_view, name='grade_answer'),

    path('student-profile/', views.student_profile_view, name='student-profile'),
    path('teacher-profile/', views.teacher_profile_view, name='teacher-profile'),

    path('logout/', views.logout_view, name='logout'),
]