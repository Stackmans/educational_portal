from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Subject, Course


class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['photo']


class CourseForm(Course):

    courses = Course.objects.all()

    # Створити список кортежів для варіантів вибору
    course_choices = [(course.id, str(course)) for course in courses]

    # Використовуйте course_choices як choices для поля вибору
    course = forms.ChoiceField(choices=course_choices)


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
