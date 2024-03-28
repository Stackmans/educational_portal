from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from educationalportal.webeducation.models import Student, Teacher


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'photo']


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'photo']


class UserRegistrationForm(UserCreationForm):
    ROLES_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = forms.ChoiceField(choices=ROLES_CHOICES)

    # Додано поля 'first_name', 'last_name', 'email' до форми
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'role', 'password1', 'password2']

    def save(self, commit=True):
        role = self.cleaned_data['role']
        if role == 'teacher':
            user = Teacher.objects.create_user(**self.cleaned_data)
        else:
            user = Student.objects.create_user(**self.cleaned_data)
        return user
