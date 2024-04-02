from django.contrib.auth.models import AbstractUser
from django.db import models


class Course(models.Model):
    number = models.IntegerField()


class Subject(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Task(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    theme = models.CharField(max_length=200)
    description = models.TextField()


class CustomUser(AbstractUser):
    # Додати поле "role"
    role = models.CharField(max_length=7)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)

    def __str__(self):
        return self.username


class UploadsModel(models.Model):
    file = models.FileField(upload_to='uploads_model')


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher')
    subjects = models.ManyToManyField(Subject)


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student')
    subjects = models.ManyToManyField(Subject)


# class Comment(models.Model):
#     post = models.
#     author = models.
#     text = models.
#     created_at = models.
