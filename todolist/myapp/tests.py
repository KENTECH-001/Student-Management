from django.test import TestCase
from .models import Student
from django.core.exceptions import ValidationError

# Create your tests here.
class StudentModelTest(TestCase):

    def test_invalid_student(self):
        student = Student(
            student_id="STU001",
            firstName="Ahmed",
            surname="Kehinde",
            middleName="Oluwaseun",
            email="ahmed@example.com",
            studentClass="100L",
            gender="Male"
        )
        with self.assertRaises(ValidationError):
            student.full_clean()
            student.save()
