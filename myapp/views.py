from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, Teacher, Student_attendance, StudentLogin, SchoolClass, Subject, StudentResult
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


def register_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        full_name=request.POST.get('fullname')
        email=request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if User.objects.filter(is_superuser=True).exists():
            messages.error(request, 'The Admin is already created. Login instead.')
            return redirect('login_admin')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register_admin')

        user = User.objects.create_superuser(
            username=username,
            first_name=full_name,
            email=email,
            password=password
        )
        messages.success(request, 'Admin account created successfully!')
        return redirect('login_admin')

    return render(request, 'register_admin.html')



def is_admin(user):
    return user.is_authenticated and user.is_superuser


def admin_required(view_func):
    return user_passes_test(
        is_admin,
        login_url='login_admin'
    )(view_func)



def is_teacher(user):
    return user.is_authenticated and hasattr(user, 'teacher')


def teacher_required(view_func):
    return user_passes_test(
        is_teacher, login_url='login_teacher'
    )(view_func)



def login_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(
            username=username,
            password=password
        )
        if user is not None and user.is_superuser:
            auth.login(request, user)
            return redirect('admin_dashboard')
        messages.error(request, 'Invalid Credentials')
        return redirect('login_admin')

    return render(request, 'login_admin.html')



@admin_required
@user_passes_test(is_admin)
def register_teacher(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        assigned_class = request.POST.get('assigned_class')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'The passwords do not match!')
            return redirect('register_teacher')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register_teacher')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('register_teacher')

        with transaction.atomic():
            user = User.objects.create_user(
            username=username,
            first_name=fullname,
            email=email,
            password=password
            )

        school_class = SchoolClass.objects.get(name=assigned_class)

        Teacher.objects.create(
        user=user,
        assigned_class=school_class,
        gender=gender
    )
        messages.success(request, 'Teacher successfully registered!')
        return redirect('admin_dashboard')

    return render(request, 'register_teacher.html')



@admin_required
@user_passes_test(is_admin)
def list_teacher(request):
    teachers=Teacher.objects.select_related('user', 'assigned_class').all()
    return render (request, 'list_teacher.html', {'teachers':teachers})




@admin_required
@user_passes_test(is_admin)
def update_teacher(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        teacher = get_object_or_404(
            Teacher,
            user__username=username
        )

        teacher.user.first_name = request.POST.get('fullname')
        teacher.user.email = request.POST.get('email')
        teacher.gender = request.POST.get('gender')

        teacher.assigned_class = get_object_or_404(
            SchoolClass,
            id=request.POST.get('assigned_class')
        )

        teacher.user.save()
        teacher.save()

        messages.success(
            request,
            'Teacher record updated successfully!'
        )
        return redirect('admin_dashboard')

    username = request.GET.get('username')

    if not username:
        return redirect('admin_dashboard')

    teacher = get_object_or_404(
        Teacher,
        user__username=username
    )

    classes = SchoolClass.objects.all()

    return render(
        request,
        'update_teacher.html',
        {
            'details': teacher,
            'classes': classes
        }
    )

@admin_required
@user_passes_test(is_admin)
def list_update_teacher(request):
    teachers = Teacher.objects.select_related('user', 'assigned_class').all()
    return render(request, 'list_update_teacher.html', {'data':teachers})


@admin_required
@user_passes_test(is_admin)
def list_delete_teacher(request):
    teachers = Teacher.objects.select_related('user', 'assigned_class').all()
    return render(request, 'list_delete_teacher.html', {'data':teachers})



@admin_required
@user_passes_test(is_admin)
def delete_teacher(request):

    if request.method == 'POST':
        username = request.POST.get('username')

        teacher = get_object_or_404(
            Teacher,
            user__username=username
        )

        teacher.user.delete()

        messages.success(
            request,
            'Teacher deleted successfully!'
        )

        return redirect('admin_dashboard')

    username = request.GET.get('username')

    if username:
        teacher = get_object_or_404(
            Teacher,
            user__username=username
        )

        return render(
            request,
            'delete_teacher.html',
            {'details': teacher}
        )

    return redirect('admin_dashboard')


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

    student_id = request.session.get('student_id')
    student = Student.objects.filter(student_id=student_id).first()

    if not student:
        return redirect('confirm_student_id')

    if StudentLogin.objects.filter(student=student).exists():
        messages.error(request, 'Account already exists!')
        return redirect('confirm_student_id')

    if User.objects.filter(username=student.student_id).exists():
        messages.error(request, 'An account with this Student ID already exists.')
        return redirect('confirm_student_id')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords don't match!")
            return redirect('register_student')

        with transaction.atomic():
            user = User.objects.create_user(
                username=student.student_id,
                password=password,
                email=student.email
            )

            StudentLogin.objects.create(
                student=student,
                user=user
            )

        request.session.pop('student_id', None)
        request.session.pop('verification_passed', None)

        messages.success(request, 'Account created successfully!')
        return redirect('login_student')

    return render(request, 'register_student.html')



def login_student(request):
    if request.method == 'POST':
        username = request.POST.get('student_id')
        password = request.POST.get('password')

        user = auth.authenticate(
            username=username,
            password=password
        )

        if user is not None:
            if hasattr(user, 'student_login'):
                auth.login(request, user)
                return redirect('student_dashboard')

            messages.error(
                request,
                'This account is not a student account!'
            )
            return redirect('login_student')

        messages.error(request, 'Invalid Credentials')
        return redirect('login_student')
    return render(request, 'login_student.html')


@admin_required
@user_passes_test(is_admin)
def new_student(request):
    if request.method == 'POST':
        student_ID = request.POST.get('student_ID')
        class_id = request.POST.get('student_class')

        if Student.objects.filter(student_id=student_ID).exists():
            messages.error(request, 'Student ID already exists!')
            return redirect('new_student')

        school_class = get_object_or_404(
            SchoolClass,
            id=class_id
        )

        Student.objects.create(
            student_id=student_ID,
            firstName=request.POST.get('student_firstName'),
            surname=request.POST.get('student_surname'),
            middleName=request.POST.get('student_middleName'),
            email=request.POST.get('student_email'),
            assigned_class=school_class,
            gender=request.POST.get('student_gender')
        )

        messages.success(
            request,
            'You have successfully added the student!'
        )

        return redirect('admin_dashboard')

    return render(request, 'new_student.html')



def login_teacher(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(
            username=username,
            password=password
        )

        if user is not None:
            if hasattr(user, 'teacher'):
                auth.login(request, user)
                return redirect('teacher_dashboard')

            messages.error(
                request,
                'This account is not a teacher account!'
            )
            return redirect('login_teacher')

        messages.error(request, 'Invalid credentials!')
        return redirect('login_teacher')

    return render(request, 'login_teacher.html')



@login_required(login_url='login_student')
def student_dashboard(request):
    if not hasattr(request.user, 'student_login'):
        return redirect('role')

    student = request.user.student_login.student

    return render(
        request,
        'student_dashboard.html',
        {'student': student}
    )



@login_required(login_url='login_teacher')
def teacher_dashboard(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('role')

    teacher = request.user.teacher

    return render(
        request,
        'teacher_dashboard.html',
        {'teacher': teacher}
    )




def logout(request):
    auth.logout(request)
    messages.success(request, 'You have successfully logged out!')
    return redirect('index')



@never_cache
@admin_required
def admin_dashboard(request):
    students = Student.objects.all()
    teachers = Teacher.objects.all()

    return render(
        request,
        'admin_dashboard.html',
        {'names': students, 'list': teachers}
    )

@admin_required
def student_details(request):
    search = request.GET.get('search')
    search_data = Student.objects.filter(student_id=search)
    return render(request, 'student_details.html', {'details': search_data})


@admin_required
def update_student(request):
    if request.method == 'POST':
        student_id = request.POST.get('id')
        data = get_object_or_404(Student, student_id=student_id)

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
            data = get_object_or_404(Student, student_id=student_id)
            return render(request, 'update_student.html', {'details': data})

        else:
            messages.error(request, 'Student Not Found')
            return redirect('update_student')

    return render(request, 'update_student.html')



@admin_required
def delete_student(request):
    if request.method =='POST':
        student_id = request.POST.get('id')
        data = get_object_or_404(Student, student_id=student_id)
        data.delete()
        messages.success(request, 'Student Deleted Successfully!')
        return redirect('admin_dashboard')

    student_id =  request.GET.get('id')

    if student_id:
        data = Student.objects.filter(student_id=student_id).first()
        return render(request, 'delete_student.html', {'detail':data})
    return render(request, 'delete_student.html')



@admin_required
def student_class(request):
    return render(request, 'student_class.html')



@admin_required
def SS1(request):
    tb1 = Student.objects.filter(assigned_class__name='SS1').values()
    return render(request, 'SS1.html', {'tb1': tb1})

@admin_required
def SS2(request):
    tb2 = Student.objects.filter(assigned_class_name='SS2').values()
    return render(request, 'SS2.html', {'tb2':tb2})


@admin_required
def SS3(request):
    tb3 = Student.objects.filter(assigned_class_name='SS3').values()
    return render(request, 'SS3.html', {'tb3':tb3})


@admin_required
def JSS1(request):
    tb4 = Student.objects.filter(assigned_class_name='JSS1').values()
    return render(request, 'JSS1.html', {'tb4':tb4})


@admin_required
def JSS2(request):
    tb5 = Student.objects.filter(assigned_class_name='JSS2').values()
    return render(request, 'JSS2.html', {'tb5':tb5})


@admin_required
def JSS3(request):
    tb6 = Student.objects.filter(assigned_class_name='JSS3').values()
    return render(request, 'JSS3.html', {'tb6':tb6})


@admin_required
def list_students(request):
    names = Student.objects.all().values()
    return render (request, 'list_students.html', {'names':names})

@admin_required
def count(request):
    count1 = Student.objects.filter(assigned_class__name='JSS1').count()
    count2 = Student.objects.filter(assigned_class__name='JSS2').count()
    count3 = Student.objects.filter(assigned_class__name='JSS3').count()
    count4 = Student.objects.filter(assigned_class__name='SS1').count()
    count5 = Student.objects.filter(assigned_class__name='SS2').count()
    count6 = Student.objects.filter(assigned_class__name='SS3').count()

    return render(request, 'count.html', {
        'count1': count1,'count2': count2,'count3': count3,'count4': count4,'count5': count5,'count6': count6
    })




@teacher_required
def student_attendance(request):
    teacher = request.user.teacher
    today = timezone.localdate()

    if teacher.assigned_class is None:
        students = Student.objects.none()
    else:
        students = Student.objects.filter(
            assigned_class=teacher.assigned_class
        )

    attendance_records = Student_attendance.objects.filter(
        student__in=students,
        date=today
    )

    attendance_data = {
        record.student_id: record.status
        for record in attendance_records
    }

    for student in students:
        student.today_status = attendance_data.get(student.id)

    return render(request, 'attendance.html', {
        'students': students
    })




@teacher_required
def choose_attendance(request):
    if request.method != 'POST':
        return redirect('student_attendance')

    teacher = request.user.teacher

    student_id = request.POST.get('student_id')
    status = request.POST.get('status')
    if not student_id:
        messages.error(request, 'Please select a student.')
        return redirect('student_attendance')

    valid_statuses = dict(Student_attendance.STATUS_CHOICES)

    if status not in valid_statuses:
        messages.error(request, 'Invalid attendance status.')
        return redirect('student_attendance')

    if teacher.assigned_class is None:
        messages.error(request, 'You have not been assigned a class.')
        return redirect('student_attendance')

    student = get_object_or_404(
        Student,
        student_id=student_id,
        assigned_class=teacher.assigned_class
    )

    today = timezone.localdate()

    Student_attendance.objects.update_or_create(
        student=student,
        date=today,
        defaults={'status': status}
    )

    messages.success(
        request,
        f'{student.firstName} attendance marked as {status}.'
    )

    return redirect('student_attendance')



@login_required(login_url='login_teacher')
def my_students(request):

    if not hasattr(request.user, 'teacher'):
        return redirect('role')

    teacher = request.user.teacher

    if teacher.assigned_class is None:
        messages.error(request, 'You have not been assigned a class!')
        return redirect('teacher_dashboard')

    students = Student.objects.filter(
        assigned_class=teacher.assigned_class
    )

    return render(request, 'my_students.html', {
        'students': students
    })



@login_required(login_url='login_teacher')
def add_results(request):
    teacher = request.user.teacher

    if teacher.assigned_class is None:
        messages.error(request, 'You have not been assigned a class.')
        return redirect('teacher_dashboard')

    students = Student.objects.filter(
        assigned_class=teacher.assigned_class
    )

    class_name = teacher.assigned_class.name

    if class_name.startswith('JSS'):
        subjects = Subject.objects.filter(school_level='Junior')
    else:
        subjects = Subject.objects.filter(school_level='Senior')

    if request.method == 'POST':
        try:
            student_id = request.POST.get('student')
            subject_id = request.POST.get('subject')
            session = request.POST.get('session')
            term = request.POST.get('term')

            test = int(request.POST.get('test'))
            exam = int(request.POST.get('exam'))

            if not (0 <= test <= 40):
                messages.error(request, 'Test mark must be between 0 and 40.')
                return redirect('add_results')

            if not (0 <= exam <= 60):
                messages.error(request, 'Exam mark must be between 0 and 60.')
                return redirect('add_results')

            student = get_object_or_404(
                students,
                student_id=student_id
            )

            subject = get_object_or_404(
                subjects,
                id=subject_id
            )

            if not session or len(session) != 9:
                messages.error(request, 'Enter a valid session, e.g. 2026/2027.')
                return redirect('add_results')

            if term not in dict(StudentResult.TERM_CHOICES):
                messages.error(request, 'Select a valid term.')
                return redirect('add_results')

            total = test + exam

            if total >= 70:
                grade = 'A'
            elif total >= 60:
                grade = 'B'
            elif total >= 50:
                grade = 'C'
            elif total >= 45:
                grade = 'D'
            elif total >= 40:
                grade = 'E'
            else:
                grade = 'F'

            StudentResult.objects.update_or_create(
                student=student,
                subject=subject,
                session=session,
                term=term,
                defaults={
                    'test': test,
                    'exam': exam,
                    'total': total,
                    'grade': grade
                }
            )

            messages.success(request, 'Student result saved successfully!')

            return redirect('add_results')

        except (ValueError, TypeError):
            messages.error(request, 'Please enter valid marks.')

    return render(request, 'add_results.html', {
        'students': students,
        'subjects': subjects,
        'teacher': teacher
    })




@login_required(login_url='login_student')
def student_view_results(request):
    if not hasattr(request.user, 'student_login'):
        return redirect('role')

    student = request.user.student_login.student

    results = StudentResult.objects.filter(
        student=student
    ).select_related('subject').order_by(
        '-session', 'term', 'subject__name'
    )

    sessions = StudentResult.objects.filter(
        student=student
    ).values_list(
        'session', flat=True
    ).distinct().order_by('-session')

    selected_session = request.GET.get('session')
    selected_term = request.GET.get('term')

    if selected_session:
        results = results.filter(session=selected_session)

    if selected_term:
        results = results.filter(term=selected_term)

    return render(request, 'student_view_results.html', {
        'results': results,
        'sessions': sessions,
        'selected_session': selected_session,
        'selected_term': selected_term,
        'student': student,
        'terms': StudentResult.TERM_CHOICES
    })



@admin_required
def admin_view_results(request):

    results = StudentResult.objects.select_related(
        'student',
        'student__assigned_class',
        'subject'
    ).all().order_by(
        '-session', 'term', 'student__surname'
    )

    classes = SchoolClass.objects.all().order_by('name')

    sessions = StudentResult.objects.values_list(
        'session', flat=True
    ).distinct().order_by('-session')

    selected_class = request.GET.get('class')
    selected_student = request.GET.get('student')
    selected_session = request.GET.get('session')
    selected_term = request.GET.get('term')

    if selected_class:
        results = results.filter(
            student__assigned_class__id=selected_class
        )

    if selected_student:
        results = results.filter(
            student__student_id=selected_student
        )

    if selected_session:
        results = results.filter(session=selected_session)

    if selected_term:
        results = results.filter(term=selected_term)

    students = Student.objects.all().order_by('surname', 'firstName')

    return render(request, 'admin_view_results.html', {
        'results': results,
        'classes': classes,
        'students': students,
        'sessions': sessions,
        'terms': StudentResult.TERM_CHOICES,
        'selected_class': selected_class,
        'selected_student': selected_student,
        'selected_session': selected_session,
        'selected_term': selected_term,
    })




@teacher_required
def teacher_view_results(request):
    teacher = request.user.teacher

    if teacher.assigned_class is None:
        messages.error(request, 'You have not been assigned a class.')
        return redirect('teacher_dashboard')

    students = Student.objects.filter(
        assigned_class=teacher.assigned_class
    )

    results = StudentResult.objects.filter(
        student__in=students
    ).select_related(
        'student', 'subject'
    ).order_by(
        '-session', 'term', 'student__surname'
    )

    sessions = results.values_list(
        'session', flat=True
    ).distinct().order_by('-session')

    selected_student = request.GET.get('student')
    selected_session = request.GET.get('session')
    selected_term = request.GET.get('term')

    if selected_student:
        results = results.filter(
            student__student_id=selected_student
        )

    if selected_session:
        results = results.filter(session=selected_session)

    if selected_term:
        results = results.filter(term=selected_term)

    return render(request, 'teacher_view_results.html', {
        'results': results,
        'students': students,
        'sessions': sessions,
        'terms': StudentResult.TERM_CHOICES,
        'selected_student': selected_student,
        'selected_session': selected_session,
        'selected_term': selected_term,
        'teacher': teacher
    })




@admin_required
def upload_timetable(request):

    classes = SchoolClass.objects.all().order_by('name')

    if request.method == 'POST':
        class_id = request.POST.get('school_class')
        timetable_image = request.FILES.get('image')

        school_class = get_object_or_404(
            SchoolClass,
            id=class_id
        )

        if not timetable_image:
            messages.error(request, 'Please select a timetable image.')
            return redirect('upload_timetable')

        timetable, created = Timetable.objects.get_or_create(
            school_class=school_class,
            defaults={'image': timetable_image}
        )

        if not created:
            timetable.image = timetable_image
            timetable.save()

        messages.success(
            request,
            f'{school_class.name} timetable uploaded successfully!'
        )

        return redirect('upload_timetable')

    timetables = Timetable.objects.select_related(
        'school_class'
    ).all()

    return render(request, 'upload_timetable.html', {
        'classes': classes,
        'timetables': timetables
    })




@teacher_required
def teacher_timetable(request):

    teacher = request.user.teacher

    if teacher.assigned_class is None:
        messages.error(request, 'You have not been assigned a class.')
        return redirect('teacher_dashboard')

    timetable = Timetable.objects.filter(
        school_class=teacher.assigned_class
    ).first()

    return render(request, 'teacher_timetable.html', {
        'teacher': teacher,
        'timetable': timetable
    })




@login_required(login_url='login_student')
def student_timetable(request):

    if not hasattr(request.user, 'student_login'):
        return redirect('role')

    student = request.user.student_login.student

    timetable = Timetable.objects.filter(
        school_class=student.assigned_class
    ).first()

    return render(request, 'student_timetable.html', {
        'student': student,
        'timetable': timetable
    })





# @api_view (['GET'])
# @permission_classes([IsAuthenticated])
# def view(request):
#     students= Student.objects.all()
#     serializer = StudentSerializer(students, many=True)
#     return Response(serializer.data)

# @api_view(['POST'])
# def create_api(request):
#     serializer= StudentSerializer(
#         data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(
#             serializer.data,
#                 status=status.HTTP_201_CREATED)
#     return Response(
#         serializer.errors,
#                 status=status.HTTP_400_BAD_REQUEST)

# @api_view(['PUT'])
# def update_api(request, id):
#     student=Student.objects.get(id=id)
#     serializer=StudentSerializer(student,
#         data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(
#             serializer.data,
#                 status=status.HTTP_200_OK)
#     return Response(
#         serializer.errors,
#             status=status.HTTP_400_BAD_REQUEST)

# @api_view(['PATCH'])
# def patch_api(request, id):
#     student=Student.objects.get(id=id)
#     serializer=StudentSerializer(student,
#         data=request.data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(
#             serializer.data,
#                 status=status.HTTP_200_OK)
#     return Response(
#         serializer.errors,
#             status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def read_api(request, id):
#     try:
#         student=Student.objects.get(id=id)
#     except Student.DoesNotExist:
#         return Response(
#             {"error":"Student Not Found"},
#              status=status.HTTP_404_NOT_FOUND)
#     serializer=StudentSerializer(student)
#     return Response(serializer.data)


# @api_view(['DELETE'])
# def delete_api(request, id):
#     try:
#         student=Student.objects.get(id=id)

#     except Student.DoesNotExist:
#         return Response(
#             {"error": "Student Not Found"},
#             status=status.HTTP_404_NOT_FOUND)
#     student.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)

    


    

    













    


    
