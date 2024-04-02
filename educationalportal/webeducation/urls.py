from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('account/', views.check_account, name='check_account'),
    path('add_subject_to_user/', views.add_subject_to_user, name='add_subject_to_user')

    # path('add_subjects/', views.add_subject_page, name='add_subjects'),
    # path('add_subject/', views.add_subject_page, name='add_subject_page'),
]
