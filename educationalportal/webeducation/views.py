from django.http import HttpResponse
from django.shortcuts import render


info = {
    'title': 'Enlighten me'
}


def index(request):
    return render(request, 'webeducation/index.html', info)
