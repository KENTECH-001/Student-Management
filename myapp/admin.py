from django.contrib import admin
from . import models
from myapp.models import Teacher, Student, SchoolClass

# Register your models here.
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(SchoolClass)

