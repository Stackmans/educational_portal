from django.shortcuts import get_object_or_404

from .models import SubjectRequest, Course
from .models import Quiz


def unconfirmed_requests(request):
    if request.user.is_authenticated and request.user.role == 'teacher':
        has_unconfirmed_requests = SubjectRequest.objects.filter(teacher=request.user.teacher,
                                                                 is_confirmed=False).exists()
        print(has_unconfirmed_requests)
    else:
        has_unconfirmed_requests = False
    return {'has_unconfirmed_requests': has_unconfirmed_requests}


# hasattr?
def check_student_quizzes(request):
    if request.user.is_authenticated and hasattr(request.user, 'student'):
        student = request.user.student
        if student.course:
            student_course = get_object_or_404(Course, id=student.course.id)
            # Додайте необхідну логіку для перевірки студентських вікторин
        else:
            student_course = None
    else:
        student_course = None

    return {'student_course': student_course}
