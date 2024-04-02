from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Subject


class RegisterUserForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher')])

    class Meta:
        model = CustomUser
        fields = ('username', 'role', 'first_name', 'last_name', 'email', 'password1', 'password2')


class SubjectDisplayForm(forms.Form):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False)
