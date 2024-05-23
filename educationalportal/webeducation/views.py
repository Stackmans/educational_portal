from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from .forms import RegisterUserForm, SubjectDisplayForm, DeleteAccountForm, PhotoUploadForm, AddTaskForm, \
    CustomUserChangeForm, TaskSolutionForm
from .models import CustomUser, Teacher, Student, Subject, Course, SubjectRequest, Task, TaskSolution
from .utils import add_subject

info = {
    'title': 'Enlighten me'
}


class UploadPhotoView(View):
    def post(self, request):
        form = PhotoUploadForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('check_account')
        return render(request, 'webeducation/upload_photo.html', {'form': form})


class AccountInfo(View):
    def get(self, request):
        subjects = Subject.objects.all()
        context = {'subjects': subjects}
        return render(request, 'webeducation/account_info.html', context)


class AccountEditView(View):
    def get(self, request):
        courses = Course.objects.all()
        form = CustomUserChangeForm(instance=request.user)
        context = {
            'courses': courses,
            'form': form
        }
        return render(request, 'webeducation/account_edit.html', context)

    def post(self, request):
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('check_account')  # Перенаправлення на успішну сторінку
        return render(request, 'webeducation/account_edit.html', {'form': form})


class StudentsList(View):
    def get(self, request, subject_id):
        subject = Subject.objects.get(id=subject_id)
        students = Student.objects.filter(subjects=subject)
        context = {'subject': subject, 'students': students}
        return render(request, 'webeducation/view_students.html', context)


class IndexView(View):
    def get(self, request):
        form = SubjectDisplayForm()
        context = {
            'form': form,
            'info': info
        }
        return render(request, 'webeducation/index.html', context)


# try to create decorator to check for a student
class TaskSolvingView(View):
    def get(self, request, subject_name, task_id):
        form = TaskSolutionForm()
        subject = get_object_or_404(Subject, name=subject_name)
        task = get_object_or_404(Task, id=task_id)

        # Перевірка, чи вже була відправлена відповідь для цього завдання та студента
        solution_submitted = TaskSolution.objects.filter(student=request.user.student, task=task).exists()

        context = {'subject': subject, 'form': form, 'task': task, 'solution_submitted': solution_submitted}
        return render(request, 'webeducation/task_solution.html', context)

    def post(self, request, subject_name, task_id):
        form = TaskSolutionForm(request.POST, request.FILES)
        subject = get_object_or_404(Subject, name=subject_name)
        task = get_object_or_404(Task, id=task_id)

        # Перевірка, чи вже була відправлена відповідь для цього завдання та студента
        solution_submitted = TaskSolution.objects.filter(student=request.user.student, task=task).exists()

        context = {'subject': subject, 'form': form, 'task': task, 'solution_submitted': solution_submitted}
        if form.is_valid():
            solution = form.save(commit=False)
            solution.subject = subject
            solution.student = request.user.student
            solution.task_id = task_id
            if not solution.solution_text and not solution.solution_file:
                messages.error(request, 'You can not save solution with no info.')
                return redirect('check_account')
            solution.save()
            messages.success(request, 'Solution saved successfully.')
            return redirect('check_account')
        return render(request, 'webeducation/task_solution.html', context)


class SubjectTasksView(View):
    def get(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id)
        tasks = Task.objects.filter(subject=subject)
        courses = Course.objects.all()
        user = request.user

        has_teacher = False
        if user.role == 'student':
            # Перевірка наявності підтвердженого запиту у студента для викладача з даного предмета
            has_teacher = SubjectRequest.objects.filter(
                student=user.student,
                subject=subject,
                is_confirmed=True
            ).exists()

            if user.student.course:
                tasks = tasks.filter(course_num=user.student.course)

        context = {
            'subject': subject,
            'tasks': tasks,
            'courses': courses,
            'has_teacher': has_teacher,
        }
        return render(request, 'webeducation/subject_tasks.html', context)


class SubjectTeacherTasksView(View):
    def get(self, request, subject_id, course_id):
        subject = get_object_or_404(Subject, id=subject_id)
        course = get_object_or_404(Course, id=course_id)

        context = {'subject': subject, 'course': course}
        return render(request, 'webeducation/subject_teacher_tasks.html', context)


class SolutionsView(View):
    def get(self, request, subject_name, task_id):
        task = get_object_or_404(Task, id=task_id)
        subject = get_object_or_404(Subject, name=subject_name)

        context = {'task': task, 'subject': subject}
        return render(request, 'webeducation/view_solutions.html', context)


class CheckSolutionView(View):
    def get(self, request, task_id, solution_id):
        solution = get_object_or_404(TaskSolution, id=solution_id)
        task = get_object_or_404(Task, id=task_id)
        solutions = TaskSolution.objects.filter(task=task)

        context = {'task': task, 'solutions': solutions, 'solution': solution}
        return render(request, 'webeducation/view_solution.html', context)

    def post(self, request, task_id, solution_id):
        solution = get_object_or_404(TaskSolution, id=solution_id)
        task = get_object_or_404(Task, id=task_id)
        solutions = TaskSolution.objects.filter(task=task)

        context = {'task': task, 'solutions': solutions, 'solution': solution}
        return render(request, 'webeducation/view_solution.html', context)


class AddTaskView(View):
    def get(self, request):
        form = AddTaskForm()
        return render(request, 'webeducation/add_task.html', {'form': form})

    def post(self, request):
        form = AddTaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            task.save()
            return redirect('check_account')

        return render(request, 'webeducation/add_task.html', {'form': form})


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


class AddSubjectToUserView(View):
    # def get(self, request):
    #     subjects = Subject.objects.all()
    #     return render(request, 'webeducation/check_account.html', {'subjects': subjects})

    def post(self, request):
        subject_ids = request.POST.getlist('subject_id')
        for subject_id in subject_ids:
            subject = get_object_or_404(Subject, id=subject_id)
            add_subject(subject, request.user.username)
        return redirect('check_account')


class DeleteSubjectView(View):
    def get(self, request):
        return redirect('check_account')

    def post(self, request):
        user = request.user
        subject_id = request.POST.get('subject_id')
        subject = get_object_or_404(Subject, id=subject_id)

        if user.role == 'teacher':
            user.teacher.subjects.remove(subject)
        elif user.role == 'student':
            user.student.subjects.remove(subject)

        return redirect('check_account')


class FindTeacherView(View):
    def get(self, request):
        user = request.user
        subjects_with_teacher = []
        if user.is_authenticated and user.role == 'student':
            # Отримати всі запити, незалежно від того, підтверджені вони чи ні
            subjects_with_teacher = SubjectRequest.objects.filter(
                student=user.student
            ).values_list('subject_id', flat=True)

        context = {
            'subjects_with_teacher': subjects_with_teacher,
        }
        return render(request, 'webeducation/find_teacher.html', context)


def view_teachers(request, subject_name):
    subject = get_object_or_404(Subject, name=subject_name)
    student = request.user.student

    existing_request = SubjectRequest.objects.filter(student=student, subject=subject).exists()

    context = {'subject': subject, 'existing_request': existing_request}
    return render(request, 'webeducation/view_teachers.html', context)


# class TeachersListView(View):  # what??
#
#     def get_context_data(self, request, *args, **kwargs):
#         context = super().get_context_data(*args, **kwargs)
#         context['user'] = request.user
#         return context
#
#     @login_required
#     def get(self, request, subject_name):
#         subject = get_object_or_404(Subject, name=subject_name)
#         context = self.get_context_data(request, subject_name=subject_name)
#         return render(request, 'webeducation/view_teachers.html', context)
#
#     @login_required
#     def post(self, request, subject_name):
#         pass


class SelectCourseView(View):
    def get(self, request):
        courses = Course.objects.all()
        return render(request, 'webeducation/select_course.html', {'courses': courses})

    def post(self, request):
        course_id = request.POST.get('course_id')
        student = request.user.student
        student.course_id = course_id
        student.save()
        return redirect('check_account')


class RequestsView(View):
    def get(self, request):
        requests = SubjectRequest.objects.filter(is_confirmed=False)
        return render(request, 'webeducation/requests_to_teacher.html', {'requests': requests})


def confirm_request(request, request_id):  # utils?
    subject_request = get_object_or_404(SubjectRequest, pk=request_id)
    subject_request.is_confirmed = True
    subject_request.save()
    return redirect('requests')


def reject_request(request, request_id):  # utils?
    subject_request = get_object_or_404(SubjectRequest, pk=request_id)
    subject_request.delete()
    return redirect('requests')


class SendRequestView(View):
    def get(self, request):
        pass

    def post(self, request):
        teacher_id = request.POST.get('teacher_id')
        subject_id = request.POST.get('subject_id')
        student = request.user.student

        existing_request = SubjectRequest.objects.filter(student=student, teacher_id=teacher_id, subject_id=subject_id).first()
        if existing_request:
            messages.warning(request, 'You have already sent a request to this teacher for this subject.')
        else:
            SubjectRequest.objects.create(student=student, teacher_id=teacher_id, subject_id=subject_id)
            messages.success(request, 'Request sent successfully!')

        return redirect('check_account')


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

            if role == 'teacher':
                Teacher.objects.create(user=user)
            elif role == 'student':
                Student.objects.create(user=user)

            login(request, user)

            messages.success(request, 'Ви успішно зареєструвалися!')
            return redirect('check_account')
        else:
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
                return redirect('check_account')
            else:
                messages.error(request, 'Неправильний логін або пароль.')
        return render(request, 'webeducation/login.html', {'form': form})


# @method_decorator(login_required, name='dispatch')
# class DeleteAccount(View):
#     def get(self, request):
#         form = DeleteAccountForm()
#         return render(request, 'webeducation/account_info.html', {'form': form})
#
#     def post(self, request):
#         form = DeleteAccountForm(request.POST)
#         if form.is_valid() and form.cleaned_data['confirm_delete']:
#             request.user.delete()
#             return redirect('home')
#         else:
#             return render(request, 'webeducation/account_info.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class DeleteAccount(View):
    def get(self, request):
        form = DeleteAccountForm()
        return render(request, 'webeducation/account_info.html', {'form': form,})

    def post(self, request):
        form = DeleteAccountForm(request.POST)
        if form.is_valid() and form.cleaned_data['confirm_delete']:
            request.user.delete()
            return redirect('home')
        else:
            return render(request, 'webeducation/account_info.html', {'form': form,})
