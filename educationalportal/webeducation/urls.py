from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('account/', views.check_account, name='check_account'),
    path('add_subject_to_user/', views.add_subject_to_user, name='add_subject_to_user'),

    path('delete_subject/', views.DeleteSubjectView.as_view(), name='delete_subject'),

    path('delete', views.DeleteAccount.as_view(), name='delete_account'),
    # path('delete', views.delete_account, name='delete_account'),

]
