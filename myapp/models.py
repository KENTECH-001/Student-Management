from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Teacher(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher',
        null=True,
        blank=True
    )

    gender = models.CharField(max_length=10, blank=True, default='')
    assigned_class = models.CharField(max_length=10, blank=True, default='')

    class Meta:
        db_table = 'myapp_teacher'

class Student(models.Model):
    student_id = models.CharField(max_length=200, unique=True)
    firstName = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    middleName = models.CharField(max_length=200)
    email = models.EmailField(max_length=100)
    studentClass = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)
    attendance = models.BooleanField(default=True)
    registrationDate = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'myapp_student'



class StudentLogin(models.Model):
    student=models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='login'
    )
    user=models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_login'

    )

    class Meta:
        db_table='myapp_studentLogin'


class Student_attendance(models.Model):
    STATUS_CHOICES=[
        ('present', 'Present'),
        ('absent', 'Absent')
    ]
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='Student_attendance'
    )
    date= models.DateField()
    status=models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'date'],
                name='unique_student_daily_attendance'
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"
    
