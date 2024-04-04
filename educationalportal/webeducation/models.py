from django.contrib.auth.models import AbstractUser
from django.db import models


class Course(models.Model):
    course_number = models.IntegerField()

    def __str__(self):
        return f'You on {self.course_number} course'


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


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student', null=True, blank=True)
    subjects = models.ManyToManyField(Subject)
    course_number = models.ManyToManyField(Course)

# class Comment(models.Model):
#     post = models.
#     author = models.
#     text = models.
#     created_at = models.
