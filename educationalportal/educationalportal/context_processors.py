from educationalportal.webeducation.models import SubjectRequest


def unconfirmed_requests(request):
    if request.user.is_authenticated and request.user.role == 'teacher':
        has_unconfirmed_requests = SubjectRequest.objects.filter(teacher=request.user.teacher, is_confirmed=False).exists()
    else:
        has_unconfirmed_requests = False  # Set to False for non-teacher users or when not authenticated
    return {'has_unconfirmed_requests': has_unconfirmed_requests}
