from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from .models import Student, Teacher, Student_attendance
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view, permission_classes
from .serializers import StudentSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# Create your views here.
def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username Already Exists!')
                return redirect('register')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email Already Exists!')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                Teacher.objects.create(username=username, email=email, password=password)
                messages.success(request, 'You Have Successfully Registered')
                return redirect('login')
        else:
            messages.error(request, 'The Password Does Not Match!')
            return redirect('register')
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Credentials! ')
            return redirect('login')
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    messages.success(request, 'You Have Successfully Logged Out!')
    return render(request, 'index.html')

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
        return redirect('dashboard')
    return render(request, 'new_student.html')

@never_cache
@login_required(login_url='login')
def dashboard(request):
    students = Student.objects.all()
    teachers = Teacher.objects.all()
    return render(request, 'dashboard.html', {'names': students, 'list':teachers})


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
        return redirect('dashboard')
        

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
        return redirect('dashboard')

    student_id =  request.GET.get('id')

    if student_id:
        data = Student.objects.filter(student_id=student_id).first
        return render(request, 'delete_student.html', {'detail':data})
    return render(request, 'delete_student.html')


# @login_required(login_url='login')
# def all_student(request):
    
#     return render(request, 'all_student.html', {'all':all})


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

    


    

    













    


    
