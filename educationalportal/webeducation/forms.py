from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Subject, Course, Task, TaskSolution


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
    confirm_delete = forms.BooleanField(label='Підтверджую, що хочу видалити свій аккаунт', required=True)


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

