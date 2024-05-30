from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Subject, Course, Task, TaskSolution, StudentSubjectPoints, Quiz, QuizQuestion, \
    QuizOption


class SubjectRequestForm(forms.Form):
    pass


class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['photo']


class RegisterUserForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher')])

    class Meta:
        model = CustomUser
        fields = ('username', 'role', 'first_name', 'last_name', 'email', 'password1', 'password2')


class DeleteAccountForm(forms.Form):
    confirm_delete = forms.BooleanField(required=True, label='Confirm deletion')


class SubjectDisplayForm(forms.Form):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False)


class StudentCourseForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        empty_label=None,  # Прибрати пустий варіант
        label='Choose a course',
    )


class AddTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['subject', 'theme', 'description', 'course_num']


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name']


class TaskSolutionForm(forms.ModelForm):
    class Meta:
        model = TaskSolution
        fields = ['solution_text', 'solution_file']


class StudentSubjectPointsFrom(forms.ModelForm):
    class Meta:
        model = StudentSubjectPoints
        fields = ['points', 'description']


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['theme', 'course', 'time_limit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['theme'].label = 'Quiz Title'
        self.fields['time_limit'].label = 'Time Limit (minutes)'
        self.fields['time_limit'].widget.attrs['min'] = 5
        self.fields['time_limit'].widget.attrs['max'] = 60


class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['question_text']


class QuizOptionForm(forms.ModelForm):
    class Meta:
        model = QuizOption
        fields = ['option_text', 'is_correct']
