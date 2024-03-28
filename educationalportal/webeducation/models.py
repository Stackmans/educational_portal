from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class UploadsModel(models.Model):
    file = models.FileField(upload_to='uploads_model')


# class Comment(models.Model):
#     post = models.
#     author = models.
#     text = models.
#     created_at = models.


class Subject(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Student(AbstractUser):
    username = models.CharField(max_length=150, unique=True, null=False, blank=False)
    subjects_to_learn = models.ManyToManyField('Subject', related_name='students')
    photo = models.ImageField(upload_to='student_photos', null=True, blank=True)
    role = models.CharField(max_length=10, default='student')
    password = models.CharField(max_length=128, default='', null=False, blank=False)
    groups = models.ManyToManyField(Group, related_name='student_set')
    user_permissions = models.ManyToManyField(Permission, related_name='student_set')

    def is_student(self):
        return self.role == 'student'

    def get_subjects(self):
        if self.is_student():
            return self.subjects_to_learn.all()
        return None

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Teacher(AbstractUser):
    username = models.CharField(max_length=150, unique=True, null=False, blank=False)
    subjects_to_teach = models.ManyToManyField('Subject', related_name='teachers')
    photo = models.ImageField(upload_to='teacher_photos', null=True, blank=True)
    role = models.CharField(max_length=10, default='teacher')
    password = models.CharField(max_length=128, default='', null=False, blank=False)
    groups = models.ManyToManyField(Group, related_name='teacher_set')
    user_permissions = models.ManyToManyField(Permission, related_name='teacher_set')

    def is_teacher(self):
        return self.role == 'teacher'

    def get_taught_subjects(self):
        if self.is_teacher():
            return self.subjects_to_teach.all()
        return None

    def __str__(self):
        return f'{self.last_name} {self.first_name}'
