from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError


class StudentClass(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='student_profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='teacher_profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    time_limit = models.IntegerField()
    target_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('short', 'Short Answer'),
        ('long', 'Long Answer'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='mcq')
    question = models.CharField(max_length=500)

    option1 = models.CharField(max_length=200, blank=True, null=True)
    option2 = models.CharField(max_length=200, blank=True, null=True)
    option3 = models.CharField(max_length=200, blank=True, null=True)
    option4 = models.CharField(max_length=200, blank=True, null=True)

    answer = models.TextField(blank=True, null=True)
    marks = models.PositiveIntegerField(default=1)

    def clean(self):
        if self.question_type == 'mcq':
            if not all([self.option1, self.option2, self.option3, self.option4]):
                raise ValidationError("MCQ questions must have all 4 options.")
            if not self.answer:
                raise ValidationError("MCQ questions must have a correct answer.")
        else:
            self.option1 = None
            self.option2 = None
            self.option3 = None
            self.option4 = None

    def save(self, *args, **kwargs):
        if self.question_type == 'mcq':
            self.marks = 1
        elif self.question_type == 'short':
            self.marks = 2
        elif self.question_type == 'long':
            self.marks = 5

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.question} ({self.question_type})"


class QuizAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def remaining(self):
        end = self.start_time + timedelta(minutes=self.quiz.time_limit)
        return (end - timezone.now()).total_seconds()

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"


class Score(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.score}"


class StudentAnswer(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)

    is_correct = models.BooleanField(default=False)
    marks_awarded = models.IntegerField(default=0)
    checked_by_teacher = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {self.question.question[:30]}"