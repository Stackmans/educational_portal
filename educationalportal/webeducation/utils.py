from django.shortcuts import get_object_or_404
from .models import Subject, CustomUser, Quiz, QuizOption, QuizAnswer


def add_subject(subject_name, user_name):
    subject = get_object_or_404(Subject, name=subject_name)
    user = get_object_or_404(CustomUser, username=user_name)

    if user.role == 'teacher':
        teacher = user.teacher

        teacher.subjects.add(subject)

    elif user.role == 'student':
        student = user.student

        student.subjects.add(subject)

    else:
        raise ValueError('Invalid user role')


def save_quiz_answers(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if request.method == 'POST':
        for question in quiz.questions.all():
            chosen_option_id = request.POST.get(f'question_{question.id}')
            if chosen_option_id:
                chosen_option = get_object_or_404(QuizOption, pk=chosen_option_id)
            else:
                chosen_option = None  # або можна просто пропустити збереження, якщо нічого не обрано
            QuizAnswer.objects.update_or_create(
                student=request.user.student,
                quiz_question=question,
                defaults={'chosen_option': chosen_option}
            )
