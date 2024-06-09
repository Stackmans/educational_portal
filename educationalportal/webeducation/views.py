from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum  # wtf
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from .forms import RegisterUserForm, SubjectDisplayForm, DeleteAccountForm, PhotoUploadForm, AddTaskForm, \
    CustomUserChangeForm, TaskSolutionForm, StudentSubjectPointsFrom, QuizForm
from .models import CustomUser, Teacher, Student, Subject, Course, SubjectRequest, Task, TaskSolution, Quiz, \
    QuizQuestion, QuizOption, QuizAnswer, StudentSubjectPoints
from .utils import add_subject, save_quiz_answers

#  !!????
info = {
    'title': 'Enlighten me'
}


# ?
class UploadPhotoView(View):
    def post(self, request):
        form = PhotoUploadForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('check_account')
        return render(request, 'webeducation/upload_photo.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class AccountInfo(View):
    def get(self, request):
        subjects = Subject.objects.all()
        context = {'subjects': subjects}
        return render(request, 'webeducation/account_info.html', context)


@method_decorator(login_required, name='dispatch')
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
            return redirect('check_account')
        return render(request, 'webeducation/account_edit.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class CheckMyPointsView(View):
    def get(self, request):
        student = request.user.student
        subjects = student.subjects.all()
        subject_points = []

        for subject in subjects:
            points = student.studentsubjectpoints_set.filter(subject=subject)
            total_points = points.aggregate(total=Sum('points'))['total'] or 0
            points_with_tasks = []

            for point in points:
                task = point.task
                points_with_tasks.append({'task': task, 'points': point.points})

            subject_points.append({'subject': subject, 'points_with_tasks': points_with_tasks,
                                   'total_points': total_points})

        context = {'subject_points': subject_points}
        return render(request, 'webeducation/check_my_points.html', context)


@method_decorator(login_required, name='dispatch')
class StudentsList(View):
    def get(self, request, subject_id):
        subject = Subject.objects.get(id=subject_id)
        students = Student.objects.filter(subjects=subject)
        context = {'subject': subject, 'students': students}
        return render(request, 'webeducation/view_students.html', context)


@method_decorator(login_required, name='dispatch')
class TeacherProfileView(View):
    def get(self, request, teacher_id):
        teacher = get_object_or_404(Teacher, id=teacher_id)
        context = {'teacher': teacher}
        return render(request, 'webeducation/teacher_profile.html', context)


@method_decorator(login_required, name='dispatch')
class StudentProfileView(View):
    def get(self, request, student_id):
        student = get_object_or_404(Student, id=student_id)
        context = {'student': student}
        return render(request, 'webeducation/student_profile.html', context)


class IndexView(View):
    def get(self, request):
        form = SubjectDisplayForm()
        context = {
            'form': form,
            'info': info,
        }
        return render(request, 'webeducation/index.html', context)


@method_decorator(login_required, name='dispatch')
class TaskSolvingView(View):
    def get(self, request, subject_name, task_id):
        form = TaskSolutionForm()
        subject = get_object_or_404(Subject, name=subject_name)
        task = get_object_or_404(Task, id=task_id)
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


# login_required in url?
class SubjectTasksView(View):
    def get(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id)
        tasks = Task.objects.filter(subject=subject)
        courses = Course.objects.all()
        user = request.user

        has_teacher = False
        if user.role == 'student':
            has_teacher = SubjectRequest.objects.filter(
                student=user.student,
                subject=subject,
                is_confirmed=True
            ).exists()

            if user.student.course:
                tasks = tasks.filter(course_num=user.student.course)

        context = {'subject': subject, 'tasks': tasks, 'courses': courses, 'has_teacher': has_teacher,}
        return render(request, 'webeducation/subject_tasks.html', context)


@method_decorator(login_required, name='dispatch')
class SubjectTeacherTasksView(View):
    def get(self, request, subject_id, course_id):
        subject = get_object_or_404(Subject, id=subject_id)
        course = get_object_or_404(Course, id=course_id)

        context = {'subject': subject, 'course': course}
        return render(request, 'webeducation/subject_teacher_tasks.html', context)


@method_decorator(login_required, name='dispatch')
class SolutionsView(View):
    def get(self, request, subject_name, task_id):
        task = get_object_or_404(Task, id=task_id)
        subject = get_object_or_404(Subject, name=subject_name)

        context = {'task': task, 'subject': subject}
        return render(request, 'webeducation/view_solutions.html', context)


@method_decorator(login_required, name='dispatch')
class CheckSolutionView(View):
    # def get(self, request, task_id, solution_id):
    #     solution = get_object_or_404(TaskSolution, id=solution_id)
    #     task = get_object_or_404(Task, id=task_id)
    #     solutions = TaskSolution.objects.filter(task=task)
    #     points = StudentSubjectPoints.objects.filter(student=solution.student, task=task).first()
    #
    #     context = {
    #         'task': task,
    #         'solutions': solutions,
    #         'solution': solution,
    #         'subject': task.subject,
    #         'points': points
    #     }
    #     return render(request, 'webeducation/view_solution.html', context)
    def post(self, request, task_id, solution_id):

        solution = get_object_or_404(TaskSolution, id=solution_id)
        task = get_object_or_404(Task, id=task_id)
        solutions = TaskSolution.objects.filter(task=task)
        points = StudentSubjectPoints.objects.filter(student=solution.student, task=task).first()

        context = {'task': task, 'solutions': solutions, 'solution': solution,
                   'subject': task.subject, 'points': points}
        return render(request, 'webeducation/view_solution.html', context)


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class GiveGradeView(View):
    def get(self, request, student_id, subject_id, task_id):
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        task = get_object_or_404(Task, id=task_id)
        form = StudentSubjectPointsFrom(initial={'student': student, 'subject': subject, 'task': task})

        context = {'form': form, 'student': student, 'subject': subject, 'task': task}
        return render(request, 'webeducation/give_grade.html', context)

    def post(self, request, student_id, subject_id, task_id):
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        task = get_object_or_404(Task, id=task_id)
        form = StudentSubjectPointsFrom(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.student = student
            instance.subject = subject
            instance.task = task
            instance.save()
            messages.success(request, 'You have successfully submitted a grade.')
            return redirect('check_account')

        context = {'form': form, 'student': student, 'subject': subject, 'task': task}
        return render(request, 'webeducation/give_grade.html', context)


@method_decorator(login_required, name='dispatch')
class AddSubjectToUserView(View):
    def post(self, request):
        subject_ids = request.POST.getlist('subject_id')
        for subject_id in subject_ids:
            subject = get_object_or_404(Subject, id=subject_id)
            add_subject(subject, request.user.username)
        return redirect('check_account')


@method_decorator(login_required, name='dispatch')
class DeleteSubjectView(View):
    def post(self, request):
        user = request.user
        subject_id = request.POST.get('subject_id')
        subject = get_object_or_404(Subject, id=subject_id)

        if user.role == 'teacher':
            user.teacher.subjects.remove(subject)
        elif user.role == 'student':
            user.student.subjects.remove(subject)

        return redirect('check_account')


@method_decorator(login_required, name='dispatch')
class FindTeacherView(View):
    def get(self, request):
        user = request.user
        subjects_with_teacher = []
        if user.is_authenticated and user.role == 'student':
            subjects_with_teacher = SubjectRequest.objects.filter(
                student=user.student
            ).values_list('subject_id', flat=True)  # values_list

        context = {'subjects_with_teacher': subjects_with_teacher}
        return render(request, 'webeducation/find_teacher.html', context)


class ViewTeachers(LoginRequiredMixin, View):
    def get(self, request, subject_name):
        subject = get_object_or_404(Subject, name=subject_name)
        student = request.user.student
        existing_request = SubjectRequest.objects.filter(student=student, subject=subject).exists()

        context = {'subject': subject, 'existing_request': existing_request}
        return render(request, 'webeducation/view_teachers.html', context)

    def post(self, request, subject_name):
        subject = get_object_or_404(Subject, name=subject_name)
        student = request.user.student

        teacher_id = request.POST.get('teacher_id')
        if teacher_id is not None:
            teacher = get_object_or_404(Teacher, id=teacher_id)

            if SubjectRequest.objects.filter(student=student, subject=subject).exists():
                messages.error(request, 'You have already sent a request for this subject.')
                return redirect('check_account')
            else:
                new_request = SubjectRequest(student=student, subject=subject, teacher=teacher)
                new_request.save()
                messages.success(request, 'Request sent successfully.')
                return redirect('check_account')

        return redirect('view_teachers', subject_name=subject_name)


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class SendRequestView(View):
    def post(self, request):
        teacher_id = request.POST.get('teacher_id')
        subject_id = request.POST.get('subject_id')
        student = request.user.student

        existing_request = SubjectRequest.objects.filter(student=student, teacher_id=teacher_id,
                                                         subject_id=subject_id).first()
        if existing_request:
            messages.warning(request, 'You have already sent a request to this teacher for this subject.')
        else:
            SubjectRequest.objects.create(student=student, teacher_id=teacher_id, subject_id=subject_id)
            messages.success(request, 'Request sent successfully!')

        return redirect('check_account')


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

            user = CustomUser.objects.create_user(username=username, role=role, first_name=first_name,
                                                  last_name=last_name, email=email, password=password)
            if role == 'teacher':
                Teacher.objects.create(user=user)
            elif role == 'student':
                Student.objects.create(user=user)

            login(request, user)

            messages.success(request, 'successfully registered')
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
            return render(request, 'webeducation/account_info.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class CreateQuizView(View):
    def get(self, request):
        form = QuizForm()
        return render(request, 'webeducation/create_test.html', {'form': form})

    #  !!!???
    def post(self, request):
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.subject_id = request.POST.get('subject')
            quiz.save()

            questions = []
            for key, value in request.POST.items():
                print('key:', key)
                print('value', value)
                if key.startswith('question_'):
                    question_text = value
                    question = QuizQuestion.objects.create(quiz=quiz, question_text=question_text)
                    questions.append(question)

                    options = {
                        'A': request.POST.get(f'optionA_{key.split("_")[1]}'),
                        'B': request.POST.get(f'optionB_{key.split("_")[1]}'),
                        'C': request.POST.get(f'optionC_{key.split("_")[1]}'),
                        'D': request.POST.get(f'optionD_{key.split("_")[1]}'),
                    }
                    texts = {
                        'A': request.POST.get(f'textA_{key.split("_")[1]}'),
                        'B': request.POST.get(f'textB_{key.split("_")[1]}'),
                        'C': request.POST.get(f'textC_{key.split("_")[1]}'),
                        'D': request.POST.get(f'textD_{key.split("_")[1]}'),
                    }

                    for option_text, is_correct in options.items():
                        text = texts[option_text]
                        is_correct = True if option_text == request.POST.get(f'correct_option_{key.split("_")[1]}')else False
                        QuizOption.objects.create(question=question, option_text=option_text,
                                                  text=text, is_correct=is_correct)

            messages.success(request, 'Test saved successfully.')
            return redirect('check_account')
        return render(request, 'webeducation/create_test.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class QuizSubmissionView(View):
    def post(self, request, quiz_id):
        quiz = Quiz.objects.get(id=quiz_id)
        score = 0
        for question in quiz.questions.all():
            selected_option_id = request.POST.get('question_' + str(question.id))
            if selected_option_id:
                selected_option = QuizOption.objects.get(id=selected_option_id)
                if selected_option.is_correct:
                    score += 1

        # Save the score or show it in some way
        messages.success(request, f'Your score: {score}/{quiz.questions.count()}')
        return redirect('check_account')


@method_decorator(login_required, name='dispatch')
class SolveQuizView(View):
    def get(self, request, quiz_id, subject_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        subject = get_object_or_404(Subject, pk=subject_id)

        if 'quiz_end_time' not in request.session:
            quiz_duration = quiz.time_limit
            end_time = timezone.now() + timezone.timedelta(seconds=quiz_duration)
            request.session['quiz_end_time'] = end_time.timestamp()

        context = {'quiz': quiz, 'subject': subject,
                   'time_left': request.session['quiz_end_time'] - timezone.now().timestamp()}
        return render(request, 'webeducation/test.html', context)

    def post(self, request, quiz_id, subject_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        subject = get_object_or_404(Subject, pk=subject_id)

        if 'quiz_end_time' in request.session:
            time_left = max(0, request.session['quiz_end_time'] - timezone.now().timestamp())

            save_quiz_answers(request, quiz_id)
            if time_left == 0:
                messages.success(request, 'Your test saved automatically')
            else:
                messages.success(request, 'Your test saved successfully')
            del request.session['quiz_end_time']  # ?
            return redirect('check_account')
        else:
            save_quiz_answers(request, quiz_id)
            messages.success(request, 'Your test saved automatically')
            return redirect('check_account')


@method_decorator(login_required, name='dispatch')
class ViewQuiz(View):
    def get(self, request, quiz_id, subject_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        subject = get_object_or_404(Subject, pk=subject_id)
        questions = quiz.questions.all()
        context = {'quiz': quiz, 'questions': questions, 'subject': subject}
        return render(request, 'webeducation/view_quiz.html', context)


#  get_quizzes_for_user  ???!!!!!!!!!!!
@method_decorator(login_required, name='dispatch')
class QuizzesView(View):
    def get(self, request):
        form = SubjectDisplayForm()
        user = request.user
        quizzes = self.get_quizzes_for_user(user) if not user.is_anonymous else []
        context = {'form': form, 'info': info, 'quizzes': quizzes, 'user': user}
        return render(request, 'webeducation/index.html', context)

    def get_quizzes_for_user(self, user):
        quizzes = []
        if user.role == 'student':
            for subject in user.student.subjects.all():
                quizzes_for_subject = []
                for quiz in subject.quiz_set.all():
                    answered = QuizAnswer.objects.filter(student=user.student, quiz_question__quiz=quiz).exists()
                    quizzes_for_subject.append({'quiz': quiz, 'answered': answered})
                quizzes.append({'subject': subject, 'quizzes': quizzes_for_subject})
        elif user.role == 'teacher':
            for subject in user.teacher.subjects.all():
                quizzes_for_subject = []
                for quiz in subject.quiz_set.all():
                    quizzes_for_subject.append({'quiz': quiz})
                quizzes.append({'subject': subject, 'quizzes': quizzes_for_subject})
        return quizzes


@method_decorator(login_required, name='dispatch')
class SubjectQuizzesView(View):
    def get(self, request, subject_id):
        courses = Course.objects.all()
        subject = get_object_or_404(Subject, id=subject_id)
        quizzes = Quiz.objects.filter(subject=subject)
        context = {'subject': subject, 'quizzes': quizzes, 'courses': courses}
        return render(request, 'webeducation/subject_quizzes.html', context)


@method_decorator(login_required, name='dispatch')
class CourseQuizzesView(View):
    def get(self, request, subject_id, course_id):
        subject = Subject.objects.get(pk=subject_id)
        course = Course.objects.get(pk=course_id)
        quizzes = Quiz.objects.filter(course=course.id, subject=subject)
        return render(request, 'webeducation/course_quizzes.html', {'quizzes': quizzes,
                                                                    'subject': subject,
                                                                    'course': course})


@method_decorator(login_required, name='dispatch')
class QuizResultsView(View):
    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        quiz_answers = QuizAnswer.objects.filter(quiz_question__quiz=quiz).select_related('student')

        students = set()
        student_answers = {}
        for answer in quiz_answers:
            if answer.student_id not in students:
                students.add(answer.student_id)
                student_answers[answer.student_id] = answer

        student_names = {student_id: Student.objects.get(id=student_id).user.username for student_id in students}

        context = {'quiz': quiz, 'students': students,
                   'student_answers': student_answers, 'student_names': student_names}
        return render(request, 'webeducation/quiz_results.html', context)


@method_decorator(login_required, name='dispatch')
class CheckStudentAnswerView(View):
    def get(self, request, student_id, quiz_id):
        student_answers = QuizAnswer.objects.filter(student_id=student_id, quiz_question__quiz_id=quiz_id)
        context = {'student_answers': student_answers}
        return render(request, 'webeducation/quiz_student_answer.html', context)


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
