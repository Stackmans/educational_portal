from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Task(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    theme = models.CharField(max_length=200)
    description = models.TextField()


class CustomUser(AbstractUser):
    role = models.CharField(max_length=7)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)

    def __str__(self):
        return self.username


class UploadsModel(models.Model):
    file = models.FileField(upload_to='uploads_model')


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher', null=True, blank=True)
    subjects = models.ManyToManyField(Subject)


class Course(models.Model):
    course_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])

    def __str__(self):
        return str(self.course_number)


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student', null=True, blank=True)
    subjects = models.ManyToManyField(Subject)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username


class SubjectRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_requests')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_requests')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    is_confirmed = models.BooleanField(default=False)
