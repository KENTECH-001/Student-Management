from django.contrib import admin
from . import models
from myapp.models import Teacher, Student

# Register your models here.
admin.site.register(Teacher)
admin.site.register(Student)
