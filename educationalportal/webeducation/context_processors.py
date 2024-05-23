from .models import SubjectRequest


def unconfirmed_requests(request):
    if request.user.is_authenticated and request.user.role == 'teacher':
        has_unconfirmed_requests = SubjectRequest.objects.filter(teacher=request.user.teacher, is_confirmed=False).exists()
        print(has_unconfirmed_requests)
    else:
        has_unconfirmed_requests = False
    return {'has_unconfirmed_requests': has_unconfirmed_requests}
