from django.db import models
from django.contrib.auth.models import User

# Create your models here.\


class SchoolClass(models.Model):
    name=models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



class Teacher(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher',
        null=True,
        blank=True
    )

    assigned_class = models.OneToOneField(
        SchoolClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_teacher'
    )

    gender = models.CharField(
        max_length=10,
        blank=True,
        default=''
    )

    class Meta:
        db_table = 'myapp_teacher'




class Student(models.Model):
    student_id = models.CharField(max_length=200, unique=True)
    firstName = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    middleName = models.CharField(max_length=200)
    email = models.EmailField(max_length=100)
    gender = models.CharField(max_length=10)
    attendance = models.BooleanField(default=True)
    assigned_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='students'
    )
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


class Junior_subjects(models.Model):
    mathematics=models.IntegerField(blank=False)
    English=models.IntegerField(blank=False)
    Basic_Science=models.IntegerField(blank=False)
    Pre_Vocation=models.IntegerField(blank=False)
    Yoruba=models.IntegerField(blank=False)
    Digital_Litiracy=models.IntegerField(blank=False)
    History=models.IntegerField(blank=False)
    National_values=models.IntegerField(blank=False)
    Reiigious_studies=models.IntegerField(blank=False)
    Business_studies=models.IntegerField(blank=False)
    Creative_arts=models.IntegerField(blank=False)

    class Meta:
        db_table = 'junior_subjects'


class Senior_subjects(models.Model):
    mathematics=models.IntegerField(blank=False)
    english=models.IntegerField(blank=False)
    physics=models.IntegerField(blank=False)
    chemistry=models.IntegerField(blank=False)
    biology=models.IntegerField(blank=False)
    agric_science=models.IntegerField(blank=False)
    civic_education=models.IntegerField(blank=False)
    economics=models.IntegerField(blank=False)
    marketing=models.IntegerField(blank=False)
    commerce=models.IntegerField(blank=False)
    accounting=models.IntegerField(blank=False)
    literature=models.IntegerField(blank=False)
    government=models.IntegerField(blank=False)
    data_processing=models.IntegerField(blank=False)
    yoruba=models.IntegerField(blank=False)

    class Meta:
        db_table='senior_subjects'


    




    
