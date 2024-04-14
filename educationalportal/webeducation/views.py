from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from .forms import RegisterUserForm, SubjectDisplayForm, DeleteAccountForm, PhotoUploadForm, StudentCourseForm
from .models import CustomUser, Teacher, Student, Subject, Course, SubjectRequest, Task
from .utils import add_subject

info = {
    'title': 'Enlighten me'
}


class UploadPhotoView(View):
    def get(self, request):
        form = PhotoUploadForm(instance=request.user)
        return render(request, 'webeducation/upload_photo.html', {'form': form})

    def post(self, request):
        form = PhotoUploadForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('check_account')  # або інша сторінка
        return render(request, 'webeducation/upload_photo.html', {'form': form})


# ------------------------------СЮДИ ДОДАВАТИ КОНТЕКСТ----------------------------------------
def check_account(request):
    courses = Course.objects.all()
    subjects = Subject.objects.all()
    context = {'subjects': subjects, 'courses': courses}
    return render(request, 'webeducation/account_info.html', context)


def teacher_accounts(request):
    teachers = Teacher.objects.all()
    context = {'teachers': teachers}
    return render(request, 'webeducation/view_teachers.html', context)


def view_students(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    students = Student.objects.filter(subjects=subject)
    context = {'subject': subject, 'students': students}
    return render(request, 'webeducation/view_students.html', context)


def index(request):
    form = SubjectDisplayForm()
    content = {
        'form': form,
        'info': info
    }
    return render(request, 'webeducation/index.html', content)


def subject_tasks(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    tasks = Task.objects.filter(subject=subject)
    courses = Course.objects.all()

    # Якщо користувач - студент і вибрав курс
    if request.user.is_authenticated and request.user.role == 'student' and request.user.student.course:
        # Фільтруємо завдання за курсом студента
        tasks = tasks.filter(course_num=request.user.student.course)

    context = {'subject': subject, 'tasks': tasks, 'courses': courses}

    return render(request, 'webeducation/subject_tasks.html', context)


def subject_teacher_tasks(request, subject_id, course_id):
    subject = get_object_or_404(Subject, id=subject_id)  # try course_number(not id)
    course = get_object_or_404(Course, id=course_id)

    context = {'subject': subject, 'course': course}

    return render(request, 'webeducation/subject_teacher_tasks.html', context)


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


class DeleteSubjectView(View):
    def get(self, request):
        return redirect('check_account')

    def post(self, request):
        user = request.user
        subject_id = request.POST.get('subject_id')  # !!!!!!в шаблоні передати предмети
        subject = get_object_or_404(Subject, id=subject_id)

        if user.role == 'teacher':
            user.teacher.subjects.remove(subject)
        elif user.role == 'student':
            user.student.subjects.remove(subject)

        return redirect('check_account')


class SubjectTasks(View):

    def get(self, request):
        pass

    def post(self, request):
        pass


# class SubjectInfo(View):
#     def get(self, request):
#         pass
#
#     def post(self, request):
#         pass


def view_teachers(request, subject_name):
    subject = get_object_or_404(Subject, name=subject_name)

    return render(request, 'webeducation/view_teachers.html', {'subject': subject})


class SelectCourseView(View):
    def get(self, request):
        courses = Course.objects.all()
        return render(request, 'webeducation/select_course.html', {'courses': courses})

    def post(self, request):
        course_id = request.POST.get('course_id')
        student = request.user.student  # Assuming user is logged in and a student
        student.course_id = course_id
        student.save()
        return redirect('check_account')


def requests_info(request):
    requests = SubjectRequest.objects.filter(is_confirmed=False)

    return render(request, 'webeducation/requests_to_teacher.html', {'requests': requests})


def confirm_request(request, request_id):
    subject_request = get_object_or_404(SubjectRequest, pk=request_id)
    subject_request.is_confirmed = True
    subject_request.save()
    return redirect('requests')


class SendRequestView(View):
    def get(self, request):
        pass

    def post(self, request):
        teacher_id = request.POST.get('teacher_id')
        subject_id = request.POST.get('subject_id')
        student = request.user.student  # Assuming the user is a student

        # Check if a similar request already exists
        existing_request = SubjectRequest.objects.filter(student=student, teacher_id=teacher_id, subject_id=subject_id).first()
        if existing_request:
            messages.warning(request, 'Ви вже відправили запит цьому викладачу для цього предмета.')
        else:
            # Create a new request if it doesn't exist
            SubjectRequest.objects.create(student=student, teacher_id=teacher_id, subject_id=subject_id)
            messages.success(request, 'Запит надіслано успішно!')

        return redirect('home')


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


@method_decorator(login_required, name='dispatch')
class DeleteAccount(View):
    def get(self, request):
        form = DeleteAccountForm()
        return render(request, 'webeducation/account_info.html', {'form': form})

    def post(self, request):
        form = DeleteAccountForm(request.POST)
        if form.is_valid() and form.cleaned_data['confirm_delete']:
            request.user.delete()
            return redirect('home')
        else:
            return render(request, 'webeducation/account_info.html', {'form': form})
