from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Course(models.Model):
    course_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])

    def __str__(self):
        return str(self.course_number)


class Subject(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Task(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    theme = models.CharField(max_length=200)
    description = models.TextField()
    course_num = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.subject.name} - {self.theme}"


class CustomUser(AbstractUser):
    # CHOICES = (
    #     (1, 'student'),
    #     (2, 'teacher'),
    #
    # )
    role = models.CharField(max_length=7)  # , choices=CHOICES, default=1
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)

    def __str__(self):
        return self.username


class UploadsModel(models.Model):
    file = models.FileField(upload_to='uploads_model')


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher', null=True, blank=True)
    subjects = models.ManyToManyField(Subject)


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student', null=True, blank=True)
    subjects = models.ManyToManyField(Subject)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username


# mb add new table with confirmed requests
class SubjectRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_requests')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_requests')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    is_confirmed = models.BooleanField(default=False)


class TaskSolution(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='task_solutions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='task_solutions')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_solutions')
    solution_text = models.TextField(max_length=4000, blank=True, null=True)
    solution_file = models.FileField(upload_to='task_solutions/%Y/%m/%d/', blank=True, null=True)

    def __str__(self):
        return f"Task Solution for {self.task.theme} by {self.student.user.username}"


class StudentSubjectPoints(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    points = models.IntegerField(default=None, validators=[MinValueValidator(0), MaxValueValidator(60)])
    description = models.TextField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name} - Task: {self.task.theme} - Points: {self.points}"


class Quiz(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    course = models.IntegerField(choices=[(i, str(i)) for i in range(1, 7)])
    theme = models.CharField(max_length=200)
    description = models.TextField()
    time_limit = models.IntegerField(default=30, validators=[MinValueValidator(1), MaxValueValidator(120)])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.subject.name} - {self.theme}"


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()

    def __str__(self):
        return self.question_text


class QuizOption(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=5)
    text = models.CharField(max_length=200, blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.option_text} ({'Correct' if self.is_correct else 'Incorrect'})"


class QuizAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz_question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    chosen_option = models.ForeignKey(QuizOption, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.quiz_question.question_text}"
