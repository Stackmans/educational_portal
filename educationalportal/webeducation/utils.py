from django.shortcuts import get_object_or_404
from .models import Subject, CustomUser


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
