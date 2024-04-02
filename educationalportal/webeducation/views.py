from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from .forms import RegisterUserForm, SubjectDisplayForm
from .models import CustomUser, Teacher, Student, Subject
from .utils import add_subject

info = {
    'title': 'Enlighten me'
}


def check_account(request):
    subjects = Subject.objects.all()
    context = {'subjects': subjects}
    return render(request, 'webeducation/account_info.html', context)


def index(request):
    form = SubjectDisplayForm()
    content = {
        'form': form,
        'info': info
    }
    return render(request, 'webeducation/index.html', content)

def get_subjects(request):
    if request.user.is_authenticated:
        user = request.user
        if user.role == 'teacher':
            subjects = user.teacher.subjects.all()
        elif user.role == 'student':
            subjects = user.student.subjects.all()

        return render(request, 'webeducation/user_subjects.html', {'subjects': subjects})
    else:
        return render(request, 'webeducation/login.html')


@login_required
def add_subject_to_user(request):
    subjects = Subject.objects.all()
    if request.method == 'POST':
        subject_ids = request.POST.getlist('subject_id')
        for subject_id in subject_ids:
            subject = get_object_or_404(Subject, id=subject_id)
            add_subject(subject, request.user.username)
        return redirect('check_account')
    else:
        return render(request, 'webeducation/check_account.html', {'subjects': subjects})


# def delete_subject_from_user(request):
#     user = request.user
#     if user.role == 'teacher':
#         subjects = Teacher.subjects.all()
#         Teacher.subjects
#         for subject in subjects
#     if user.role == 'student':
#         pass


# ---------------------- User methods ----------------------

class RegisterView(View):
    def get(self, request):
        form = RegisterUserForm()
        return render(request, 'webeducation/register.html', {'form': form})

    def post(self, request):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            role = form.cleaned_data['role']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            # Збереження користувача в БД
            user = CustomUser.objects.create_user(username=username, role=role, first_name=first_name,
                                                  last_name=last_name, email=email, password=password)

            # Створення об'єкта вчителя або студента
            if role == 'teacher':
                Teacher.objects.create(user=user)
            elif role == 'student':
                Student.objects.create(user=user)
            # Відразу вхід після реєстрації
            login(request, user)

            messages.success(request, 'Ви успішно зареєструвалися!')
            return redirect('home')  # Перенаправлення на головну сторінку після реєстрації
        else:
            messages.error(request, 'Будь ласка, виправте помилки у формі.')
            return render(request, 'webeducation/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'webeducation/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # або інша сторінка після успішного входу
            else:
                messages.error(request, 'Неправильний логін або пароль.')
        return render(request, 'webeducation/login.html', {'form': form})


# delete from 2 tables
def delete_user(user_id):
    try:
        user = CustomUser.objects.get(pk=user_id)
        user.delete()

        try:
            teacher = Teacher.objects.get(user_id=user_id)
            teacher.delete()
        except Teacher.DoesNotExist:
            pass

        try:
            student = Student.objects.get(user_id=user_id)
            student.delete()
        except Student.DoesNotExist:
            pass

        return True

    except CustomUser.DoesNotExist:
        return False
