from django.contrib import admin
from .models import Quiz, Question, Score, QuizAttempt, StudentAnswer, StudentClass, StudentProfile


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('question_type', 'question', 'option1', 'option2', 'option3', 'option4', 'answer', 'marks')
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'time_limit', 'target_class', 'question_count')
    search_fields = ('title', 'description')
    list_filter = ('time_limit', 'target_class')
    fields = ('title', 'description', 'time_limit', 'target_class')
    inlines = [QuestionInline]

    def question_count(self, obj):
        return obj.question_set.count()
    question_count.short_description = 'Questions'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('short_question', 'quiz', 'question_type', 'marks', 'answer')
    search_fields = ('question', 'quiz__title')
    list_filter = ('quiz', 'question_type')
    fieldsets = (
        ('Basic Details', {
            'fields': ('quiz', 'question_type', 'question', 'marks')
        }),
        ('Options for MCQ Only', {
            'fields': ('option1', 'option2', 'option3', 'option4')
        }),
        ('Correct / Model Answer', {
            'fields': ('answer',)
        }),
    )

    def short_question(self, obj):
        return obj.question[:50]
    short_question.short_description = 'Question'


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score')
    search_fields = ('student__username', 'quiz__title')
    list_filter = ('quiz',)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'start_time', 'completed')
    search_fields = ('student__username', 'quiz__title')
    list_filter = ('completed', 'quiz')


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'question', 'marks_awarded', 'checked_by_teacher')
    search_fields = ('student__username', 'quiz__title', 'question__question')
    list_filter = ('checked_by_teacher', 'question__question_type')


@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_class')