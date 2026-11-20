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




class Subject(models.Model):
    name = models.CharField(max_length=100)
    school_level = models.CharField(
        max_length=10,
        choices=[
            ('Junior', 'Junior'),
            ('Senior', 'Senior')
        ]
    )

    def __str__(self):
        return self.name


class StudentResult(models.Model):
    TERM_CHOICES = [
        ('First Term', 'First Term'),
        ('Second Term', 'Second Term'),
        ('Third Term', 'Third Term'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='results'
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT
    )

    test = models.PositiveIntegerField()
    exam = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    grade = models.CharField(max_length=2)

    session = models.CharField(max_length=9)
    term = models.CharField(
        max_length=20,
        choices=TERM_CHOICES
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'subject', 'session', 'term'],
                name='unique_student_subject_result'
            )
        ]

    def __str__(self):
        return f'{self.student} - {self.subject} - {self.term}'

class Student_attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent')
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='Student_attendance'
    )

    date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'date'],
                name='unique_student_daily_attendance'
            )
        ]

    

class Timetable(models.Model):
    school_class = models.OneToOneField(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='timetable'
    )

    image = models.ImageField(
        upload_to='timetables/'
    )

    uploaded_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.school_class.name} Timetable'



    

class SchoolSettings(models.Model):
    school_name = models.CharField(max_length=200)
    school_logo = models.ImageField(
        upload_to='school_logo/',
        blank=True,
        null=True
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    current_session = models.CharField(max_length=9)

    current_term = models.CharField(
        max_length=20,
        choices=[
            ('First Term', 'First Term'),
            ('Second Term', 'Second Term'),
            ('Third Term', 'Third Term')
        ]
    )

    def __str__(self):
        return self.school_name