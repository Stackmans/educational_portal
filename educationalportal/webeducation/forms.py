from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegisterUserForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher')])

    class Meta:
        model = CustomUser
        fields = ('username', 'role', 'first_name', 'last_name', 'email', 'password1', 'password2')
