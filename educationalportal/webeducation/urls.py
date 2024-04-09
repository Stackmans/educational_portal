from django.conf import settings
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('account/', views.check_account, name='check_account'),
    path('account/requests', views.requests_info, name='requests'),
    path('send_request/', views.SendRequestView.as_view(), name='send_request'),
    path('confirm_request/<int:request_id>/', views.confirm_request, name='confirm_request'),

    path('add_subject_to_user/', views.add_subject_to_user, name='add_subject_to_user'),
    path('subject_info/<slug:subject_name>', views.subject_info, name='subject_info'),
    path('delete_subject/', views.DeleteSubjectView.as_view(), name='delete_subject'),
    path('delete', views.DeleteAccount.as_view(), name='delete_account'),
    path('select_course/', views.SelectCourseView.as_view(), name='select_course'),
    path('upload_photo/', views.UploadPhotoView.as_view(), name='upload_photo'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
