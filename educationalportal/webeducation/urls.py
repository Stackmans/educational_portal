from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('account/', views.AccountInfo.as_view(), name='check_account'),
    path('account/edit/', views.AccountEditView.as_view(), name='edit_account'),
    path('check_my_points/', views.CheckMyPointsView.as_view(), name='check_my_points'),
    path('view_students/<int:subject_id>/', views.StudentsList.as_view(), name='view_students'),

    # path('view_teachers/<slug:subject_name>', views.view_teachers, name='view_teachers'),
    path('view_teachers/<slug:subject_name>/', views.ViewTeachers.as_view(), name='view_teachers'),

    path('requests/', login_required(views.RequestsView.as_view()), name='requests'),
    path('send_request/', views.SendRequestView.as_view(), name='send_request'),
    path('confirm_request/<int:request_id>/', views.confirm_request, name='confirm_request'),
    path('reject_request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('add_subject_to_user/', views.AddSubjectToUserView.as_view(), name='add_subject_to_user'),
    path('subject/<int:subject_id>/', login_required(views.SubjectTasksView.as_view()), name='subject_tasks'),
    path('subject/<int:subject_id>/<int:course_id>', views.SubjectTeacherTasksView.as_view(), name='subject_teacher_tasks'),
    path('subject/<slug:subject_name>/task/<int:task_id>/', views.TaskSolvingView.as_view(), name='task_solving'),
    path('<slug:subject_name>/task/<int:task_id>/solutions/', views.SolutionsView.as_view(), name='check_solutions'),
    path('check_solution/<int:task_id>/<int:solution_id>/', views.CheckSolutionView.as_view(), name='check_solution'),
    path('give_grade/<int:student_id>/<int:subject_id>/<int:task_id>/', views.GiveGradeView.as_view(), name='give_grade'),
    path('find_teacher/', views.FindTeacherView.as_view(), name='find_teacher'),
    path('add_task/', views.AddTaskView.as_view(), name='add_task'),
    path('delete_subject/', views.DeleteSubjectView.as_view(), name='delete_subject'),
    path('delete/', views.DeleteAccount.as_view(), name='delete_account'),
    path('select_course/', views.SelectCourseView.as_view(), name='select_course'),
    path('upload_photo/', views.UploadPhotoView.as_view(), name='upload_photo'),
    path('create_quiz/', views.CreateQuizView.as_view(), name='create_quiz'),
    path('submit_quiz/<int:quiz_id>/', views.QuizSubmissionView.as_view(), name='submit_quiz'),
    path('view_quizzes/', views.QuizzesView.as_view(), name='view_quizzes'),
    path('view_quiz/<int:subject_id>/<int:quiz_id>/', views.ViewQuiz.as_view(), name='view_quiz'),
    path('solve_quiz/<int:subject_id>/<int:quiz_id>/', views.SolveQuizView.as_view(), name='solve_quiz'),

    path('subject/<int:subject_id>/quizzes/', views.SubjectQuizzesView.as_view(), name='subject_quizzes'),
    path('subject/<int:subject_id>/<int:course_id>/quizzes/', views.CourseQuizzesView.as_view(), name='course_quizzes'),

    path('quiz_results/<int:quiz_id>/', views.QuizResultsView.as_view(), name='quiz_results'),
    path('check_student_answer/<int:student_id>/<int:quiz_id>/', views.CheckStudentAnswerView.as_view(), name='check_student_answer'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
