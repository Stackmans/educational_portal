from django.contrib import admin
from .models import CustomUser, Subject, Course, Task, QuizOption, QuizQuestion, Quiz

admin.site.register(CustomUser)
admin.site.register(Subject)
admin.site.register(Course)
admin.site.register(Task)


class QuizOptionInline(admin.TabularInline):
    model = QuizOption
    extra = 4  # Кількість полів для варіантів відповідей, які можна додати одночасно


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    inlines = [QuizOptionInline]
    extra = 1  # Кількість питань, які можна додати одночасно


class QuizAdmin(admin.ModelAdmin):
    inlines = [QuizQuestionInline]


admin.site.register(Quiz, QuizAdmin)
