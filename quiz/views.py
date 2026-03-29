from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from .models import (
    Quiz,
    Question,
    Score,
    QuizAttempt,
    StudentProfile,
    TeacherProfile,
    StudentAnswer,
    StudentClass,
)


@login_required
def student_profile_view(request):
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        profile = None

    return render(request, 'quiz/student_profile.html', {'profile': profile})



@login_required
def teacher_profile_view(request):
    profile, created = TeacherProfile.objects.get_or_create(user=request.user)
    return render(request, 'quiz/teacher_profile.html', {'profile': profile})


def create_teacher_account(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        subject = request.POST.get('subject')

        if User.objects.filter(username=username).exists():
            return render(request, 'quiz/create_teacher.html', {
                'error': 'Username already exists'
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'quiz/create_teacher.html', {
                'error': 'Email already exists'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        teacher_group, created = Group.objects.get_or_create(name='Teacher')
        user.groups.add(teacher_group)

        TeacherProfile.objects.create(
            user=user,
            subject=subject
        )

        return redirect('teacherlogin')

    return render(request, 'quiz/create_teacher.html')


def register_view(request):
    classes = StudentClass.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        class_id = request.POST.get('student_class')

        if User.objects.filter(username=username).exists():
            return render(request, 'quiz/register.html', {
                'error': 'Username already exists',
                'classes': classes
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'quiz/register.html', {
                'error': 'Email already exists',
                'classes': classes
            })

        if not class_id:
            return render(request, 'quiz/register.html', {
                'error': 'Please select a class',
                'classes': classes
            })

        student_class = get_object_or_404(StudentClass, id=class_id)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        group, created = Group.objects.get_or_create(name='Student')
        user.groups.add(group)

        StudentProfile.objects.create(
            user=user,
            student_class=student_class
        )

        return redirect('studentlogin')

    return render(request, 'quiz/register.html', {'classes': classes})


def home_view(request):
    return render(request, 'quiz/home.html')


def teacher_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.groups.filter(name='Teacher').exists():
            login(request, user)
            return redirect('teacher-dashboard')
        else:
            return render(request, 'quiz/teacher_login.html', {
                'error': 'Invalid teacher username or password'
            })

    return render(request, 'quiz/teacher_login.html')


def student_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.groups.filter(name='Student').exists():
            login(request, user)
            return redirect('student-dashboard')
        else:
            return render(request, 'quiz/student_login.html', {
                'error': 'Invalid student username or password'
            })

    return render(request, 'quiz/student_login.html')


@login_required
def teacher_dashboard_view(request):
    quizzes = Quiz.objects.all()
    pending_answers = StudentAnswer.objects.filter(
        question__question_type__in=['short', 'long'],
        checked_by_teacher=False
    ).select_related('student', 'quiz', 'question')

    return render(request, 'quiz/teacher_dashboard.html', {
        'quizzes': quizzes,
        'pending_answers': pending_answers
    })


@login_required
def student_dashboard_view(request):
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return render(request, 'quiz/student_dashboard.html', {
            'quizzes': [],
            'scores': [],
            'score_data': [],
            'attempted_quiz_ids': [],
            'error': 'Your class is not assigned yet. Please contact admin.'
        })

    quizzes = Quiz.objects.filter(target_class=student_profile.student_class)
    scores = Score.objects.filter(student=request.user).select_related('quiz')
    attempts = QuizAttempt.objects.filter(student=request.user, completed=True)

    attempted_quiz_ids = [attempt.quiz.id for attempt in attempts]

    score_data = []

    for score in scores:
        questions = Question.objects.filter(quiz=score.quiz)
        total_marks = sum(q.marks for q in questions)

        percentage = 0
        if total_marks > 0:
            percentage = int((score.score / total_marks) * 100)

        score_data.append({
            'quiz': score.quiz,
            'score': score.score,
            'total_marks': total_marks,
            'percentage': percentage
        })

    return render(request, 'quiz/student_dashboard.html', {
        'quizzes': quizzes,
        'scores': scores,
        'score_data': score_data,
        'attempted_quiz_ids': attempted_quiz_ids
    })


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return redirect('student-dashboard')

    if quiz.target_class != student_profile.student_class:
        return redirect('student-dashboard')

    questions = Question.objects.filter(quiz=quiz)

    attempt, created = QuizAttempt.objects.get_or_create(
        student=request.user,
        quiz=quiz
    )

    if attempt.completed:
        return redirect('student-dashboard')

    remaining = int(attempt.remaining())
    if remaining < 0:
        remaining = 0

    if request.method == 'POST':
        score = 0

        StudentAnswer.objects.filter(student=request.user, quiz=quiz).delete()

        for q in questions:
            user_answer = request.POST.get(str(q.id), '').strip()

            answer_obj = StudentAnswer.objects.create(
                student=request.user,
                quiz=quiz,
                question=q,
                answer_text=user_answer
            )

            if q.question_type == 'mcq':
                if user_answer.lower() == (q.answer or '').strip().lower():
                    answer_obj.is_correct = True
                    answer_obj.marks_awarded = q.marks
                    answer_obj.checked_by_teacher = True
                    score += q.marks
                else:
                    answer_obj.is_correct = False
                    answer_obj.marks_awarded = 0
                    answer_obj.checked_by_teacher = True

            elif q.question_type in ['short', 'long']:
                answer_obj.is_correct = False
                answer_obj.marks_awarded = 0
                answer_obj.checked_by_teacher = False

            answer_obj.save()

        score_obj, created = Score.objects.get_or_create(
            student=request.user,
            quiz=quiz,
            defaults={'score': score}
        )

        if not created:
            score_obj.score = score
            score_obj.save()

        attempt.completed = True
        attempt.save()

        return redirect('student-dashboard')

    return render(request, 'quiz/take_quiz.html', {
        'quiz': quiz,
        'questions': questions,
        'remaining': remaining
    })


@login_required
def review_answers_view(request):
    pending_answers = StudentAnswer.objects.filter(
        question__question_type__in=['short', 'long'],
        checked_by_teacher=False
    ).select_related('student', 'quiz', 'question')

    return render(request, 'quiz/review_answers.html', {
        'pending_answers': pending_answers
    })


@login_required
def grade_answer_view(request, answer_id):
    answer = get_object_or_404(StudentAnswer, id=answer_id)

    if request.method == 'POST':
        marks = request.POST.get('marks')

        try:
            marks = int(marks)
        except (TypeError, ValueError):
            marks = 0

        if marks < 0:
            marks = 0

        if marks > answer.question.marks:
            marks = answer.question.marks

        answer.marks_awarded = marks
        answer.checked_by_teacher = True
        answer.is_correct = marks > 0
        answer.save()

        all_answers = StudentAnswer.objects.filter(
            student=answer.student,
            quiz=answer.quiz
        )

        total_score = sum(ans.marks_awarded for ans in all_answers)

        score_obj, created = Score.objects.get_or_create(
            student=answer.student,
            quiz=answer.quiz,
            defaults={'score': total_score}
        )

        if not created:
            score_obj.score = total_score
            score_obj.save()

        return redirect('review_answers')

    return render(request, 'quiz/grade_answer.html', {
        'answer': answer
    })


def logout_view(request):
    logout(request)
    return redirect('home')