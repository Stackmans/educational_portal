from django.contrib import admin
from .models import CustomUser, Subject, Course, Task


admin.site.register(CustomUser)
admin.site.register(Subject)
admin.site.register(Course)
admin.site.register(Task)

