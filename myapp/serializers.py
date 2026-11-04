from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Student
        fields= '__all__'
    def validate_student_id(self, value):
        if not value.startswith('STU'):
            raise serializers.ValidationError(
                "Student Id must start with STU")
        return value

    def validate_gender(self, value):
        if value not in ['Male', 'Female']:
            raise serializers.ValidationError(
                "Student gender must be male r female")
        return value

    def validate_studentClass(self, value):
        if value not in ['JSS1', 'JSS2', 'JSS3', 'SS1', 'SS2', 'SS3']:
            raise serializers.ValidationError(
                "Invalid Studen Class")
        return value

    def validate(self, attrs):
        if attrs['firstName'] == attrs['surname']:
            raise serializers.ValidationError(
                "The first name and the surname can't be the same"
            )
        return attrs