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
