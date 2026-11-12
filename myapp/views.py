from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, Teacher, Student_attendance, StudentLogin
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view, permission_classes
from .serializers import StudentSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.core.mail import send_mail
import secrets
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
# Create your views here.


def index(request):
    return render(request, 'index.html')

def role(request):
    return render(request, 'role.html')


def admin_registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if User.objects.filter(is_superuser=True).exists():
            messages.error(request, 'The Admin is already created. Login instead.')
            return redirect('login')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('admin_registration')

        user = User.objects.create_superuser(
            username=username,
            password=password
        )

        messages.success(request, 'Admin account created successfully!')
        return redirect('login')

    return render(request, 'register_admin.html')


def is_admin(user):
    return user.is_authenticated and user.is_superuser


def login_admin(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('passwrod')
        user=auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login_admin')
    return render(request, 'login_admin.html')



@login_required
@user_passes_test(is_admin)
def register_teacher(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'The Password Does Not Match!')
            return redirect('register_teacher')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username Already Exists!')
            return redirect('register_teacher')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email Already Exists!')
            return redirect('register_teacher')
        else:
            with transaction.atomic():
                user = User.objects.create_user(
                username=username,
                email=email,
                password=password
                )
                Teacher.objects.create(
                user=user
                )
                messages.success(request, 'Teacher Successfully Registered!')
                return redirect('login_teacher')
            
    return render(request, 'register_teacher.html')


def confirm_student_id(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')

        student = Student.objects.filter(
            student_id=student_id
        ).first()

        if not student:
            messages.error(request, 'Student ID does not exist!')
            return redirect('confirm_student_id')

        if StudentLogin.objects.filter(student=student).exists():
            messages.error(request, 'Account already exists!')
            return redirect('confirm_student_id')

        request.session['student_id'] = student.student_id
        request.session['verification_passed'] = False

        test_mail(request, student)

        return redirect('verify_student')

    return render(request, 'confirm_student_id.html')



def test_mail(request, student):
    email = student.email

    code = str(secrets.randbelow(900000) + 100000)

    request.session['verification_code'] = make_password(code)

    request.session['verification_expiry'] = (
        timezone.now() + timedelta(minutes=5)
    ).timestamp()

    send_mail(
        'Confirmation Of The Student',
        f'Your Confirmation Code is {code}',
        None,
        [email],
        fail_silently=False
    )



def verify_student(request):
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation', '').strip()

        saved_code = request.session.get('verification_code')
        expiry = request.session.get('verification_expiry')

        if not saved_code or not expiry:
            messages.error(request, 'Request a new verification code.')
            return redirect('confirm_student_id')

        if timezone.now().timestamp() > expiry:
            messages.error(request, 'Verification code has expired.')
            return redirect('confirm_student_id')

        if check_password(confirmation, saved_code):
            request.session['verification_passed'] = True

            del request.session['verification_code']
            del request.session['verification_expiry']

            return redirect('register_student')

        messages.error(request, 'Incorrect verification code!')
        return redirect('verify_student')

    return render(request, 'verify_student.html')


def register_student(request):
    if not request.session.get('verification_passed'):
        return redirect('confirm_student_id')
    student_id=request.session.get('student_id')
    student=Student.objects.filter(student_id=student_id).first()
    if not student:
        return redirect('confirm_student_id')

    if StudentLogin.objects.filter(student=student).exists():
        messages.error(request, 'Account Already Exists!')
        return redirect('confirm_student_id')

    
    if request.method=='POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords don't match!")
            return redirect('register_student')

        user = User.objects.create_user(
            username=student.student_id,
            password=password,
            email=student.email
        )

        StudentLogin.objects.create(
            student=student,
            user=user
        )

        messages.success(request, 'Account created successfully!')
        return redirect('login_student')

    return render(request, 'register_student.html')


def login_student(request):
    if request.method=='POST':
        username=request.POST.get('student_id')
        password=request.POST.get('password')
        user= auth.authenticate(username=username, password=password)

        if user is None:
            if hasattr(user, 'student_login'):
                auth.login(request, user)
                return redirect('student_dashboard')
            messages.error(request, 'This Account Is Not a Student Account')
            return redirect('login_student')

        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login_student')
    return render (request, 'login_student.html')



def new_student(request):
    if request.method == 'POST':
        student_ID = request.POST.get('student_ID')
        student_firstName = request.POST.get('student_firstName')
        student_surname = request.POST.get('student_surname')
        student_middleName = request.POST.get('student_middleName')
        student_email = request.POST.get('student_email')
        student_class = request.POST.get('student_class')
        student_gender = request.POST.get('student_gender')
        student = Student(student_id = student_ID, firstName = student_firstName, surname = student_surname, middleName = student_middleName, email = student_email, studentClass = student_class, gender = student_gender )
        student.save()
        messages.success(request, 'You Have Successfully Added The Student')
        return redirect('admin_dashboard')
    return render(request, 'new_student.html')









def login_teacher(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('teacher_dashboard')
        else:
            messages.error(request, 'Invalid Credentials! ')
            return redirect('login_teacher')
    return render(request, 'login_teacher.html')


def student_dashboard(request):
    return render (request, 'student_dashboard.html')


def teacher_dashboard(request):
    return render (request, 'teacher_dashboard.html')







def logout(request):
    auth.logout(request)
    messages.success(request, 'You Have Successfully Logged Out!')
    return render(request, 'index.html')


@never_cache
@login_required(login_url='login')
def admin_dashboard(request):
    students = Student.objects.all()
    teachers = Teacher.objects.all()
    return render(request, 'admin_dashboard.html', {'names': students, 'list':teachers})


@login_required(login_url='login')
def student_details(request):
    search = request.GET.get('search')
    search_data = Student.objects.filter(student_id=search)
    return render(request, 'student_details.html', {'details': search_data})


@login_required(login_url='login')
def update_student(request):
    if request.method == 'POST':
        student_id = request.POST.get('id')
        data = Student.objects.get(student_id=student_id)

        data.firstName = request.POST.get('firstname')
        data.surname = request.POST.get('surname')
        data.middleName =request.POST.get('middlename')
        data.email = request.POST.get('email')
        data.studentClass = request.POST.get('class')
        data.gender = request.POST.get('gender')

        data.save()
        messages.success(request, 'Student Updated Successfully!')
        return redirect('admin_dashboard')
        

    student_id = request.GET.get('id')
    

    if student_id:
        if Student.objects.filter(student_id=student_id).exists():
            data = Student.objects.get(student_id=student_id)
            return render(request, 'update_student.html', {'details': data})

        else:
            messages.error(request, 'Student Not Found')
            return redirect('update_student')

    return render(request, 'update_student.html')



@login_required(login_url='login')
def delete_student(request):
    if request.method =='POST':
        student_id = request.POST.get('id')
        data = Student.objects.get(student_id=student_id)
        data.delete()
        messages.success(request, 'Student Deleted Successfully!')
        return redirect('admin_dashboard')

    student_id =  request.GET.get('id')

    if student_id:
        data = Student.objects.filter(student_id=student_id).first
        return render(request, 'delete_student.html', {'detail':data})
    return render(request, 'delete_student.html')



@login_required(login_url='login')
def student_class(request):
    return render(request, 'student_class.html')



@login_required(login_url='login')
def SS1(request):
    tb1 = Student.objects.filter(studentClass='SS1').values()
    return render(request, 'SS1.html', {'tb1':tb1})


@login_required(login_url='login')
def SS2(request):
    tb2 = Student.objects.filter(studentClass='SS2').values()
    return render(request, 'SS2.html', {'tb2':tb2})


@login_required(login_url='login')
def SS3(request):
    tb3 = Student.objects.filter(studentClass='SS3').values()
    return render(request, 'SS3.html', {'tb3':tb3})


@login_required(login_url='login')
def JSS1(request):
    tb4 = Student.objects.filter(studentClass='JSS1').values()
    return render(request, 'JSS1.html', {'tb4':tb4})


@login_required(login_url='login')
def JSS2(request):
    tb5 = Student.objects.filter(studentClass='JSS2').values()
    return render(request, 'JSS2.html', {'tb5':tb5})


@login_required(login_url='login')
def JSS3(request):
    tb6 = Student.objects.filter(studentClass='JSS3').values()
    return render(request, 'JSS3.html', {'tb6':tb6})


@login_required(login_url='login')
def list_students(request):
    names = Student.objects.all().values()
    return render (request, 'list_students.html', {'names':names})


@login_required(login_url='login')
def count(request):
    count1=Student.objects.filter(studentClass='JSS1').count()
    count2=Student.objects.filter(studentClass='JSS2').count()
    count3=Student.objects.filter(studentClass='JSS3').count()
    count4=Student.objects.filter(studentClass='SS1').count()
    count5=Student.objects.filter(studentClass='SS2').count()
    count6=Student.objects.filter(studentClass='SS3').count()
    return render(request, 'count.html', {'count1': count1, 'count2': count2, 'count3': count3, 'count4': count4, 'count5': count5, 'count6': count6})


@login_required(login_url='login')
def attendance(request):
    data= Student.objects.all().values()
    data2= Student_attendance.objects.all().values()

    return render(request, 'attendance.html', {'datas':data, 'datas2':data2})



@api_view (['GET'])
@permission_classes([IsAuthenticated])
def view(request):
    students= Student.objects.all()
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_api(request):
    serializer= StudentSerializer(
        data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            serializer.data,
                status=status.HTTP_201_CREATED)
    return Response(
        serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_api(request, id):
    student=Student.objects.get(id=id)
    serializer=StudentSerializer(student,
        data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            serializer.data,
                status=status.HTTP_200_OK)
    return Response(
        serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def patch_api(request, id):
    student=Student.objects.get(id=id)
    serializer=StudentSerializer(student,
        data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            serializer.data,
                status=status.HTTP_200_OK)
    return Response(
        serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def read_api(request, id):
    try:
        student=Student.objects.get(id=id)
    except Student.DoesNotExist:
        return Response(
            {"error":"Student Not Found"},
             status=status.HTTP_404_NOT_FOUND)
    serializer=StudentSerializer(student)
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_api(request, id):
    try:
        student=Student.objects.get(id=id)

    except Student.DoesNotExist:
        return Response(
            {"error": "Student Not Found"},
            status=status.HTTP_404_NOT_FOUND)
    student.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

    


    

    













    


    
