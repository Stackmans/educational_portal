from django.shortcuts import get_object_or_404

from .models import SubjectRequest, Course
from .models import Quiz


def unconfirmed_requests(request):
    if request.user.is_authenticated and request.user.role == 'teacher':
        has_unconfirmed_requests = SubjectRequest.objects.filter(teacher=request.user.teacher,
                                                                 is_confirmed=False).exists()
    else:
        has_unconfirmed_requests = False
    return {'has_unconfirmed_requests': has_unconfirmed_requests}


def check_student_quizzes(request):
    if request.user.is_authenticated and hasattr(request.user, 'student') and hasattr(request.user.student, 'course'):
        student_course = get_object_or_404(Course, id=request.user.student.course.id)
        student_quizzes = Quiz.objects.filter(course=student_course.id)
    else:
        student_quizzes = None
    return {'student_quizzes': student_quizzes}
