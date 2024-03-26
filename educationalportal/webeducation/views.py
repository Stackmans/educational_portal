from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse

info = {
    'title': 'Enlighten me'
}


class RegisterView(View):

    def get(self, request):
        form = UserCreationForm()
        return render(request, 'webeducation/register.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=user.username, password=request.POST['password1'])
            if user:
                login(request, user)

            return HttpResponseRedirect(reverse('home'))
        return render(request, 'webeducation/register.html', {'form': form})


class LoginView(View):

    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'webeducation/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            # Аутентифікація користувача
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])

            # Увійти в систему користувача
            if user:
                login(request, user)
                return redirect('home')

        return render(request, 'webeducation/login.html', {'form': form, 'error_message': 'Invalid credentials'})


def index(request):
    return render(request, 'webeducation/index.html', info)
