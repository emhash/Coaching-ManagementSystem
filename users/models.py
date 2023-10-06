from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomManager
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta



class CustomUser(AbstractUser):
    username = None
    email = models.EmailField("email_address", unique=True, max_length=354)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('guardian', 'Guardian'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['phone_number']

    objects = CustomManager()



background_of_teacher = [
        ('science', 'science'),
        ('commerce', 'commerce'),
        ('arts', 'arts'),
]


class Teacher(models.Model):
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    basic_step_of_reg = models.BooleanField(default=False)
    # BASICS
    t_name = models.CharField(max_length=100)
    profile_pic = models.ImageField(upload_to="teacher", default='teacher.png')
    teacher_background = models.CharField(max_length=20, choices=background_of_teacher)
    t_present_adress = models.CharField( max_length=150, null=True, blank=True)
    t_permnt_adress = models.CharField( max_length=150, null=True, blank=True)
    t_extra_phone = models.CharField( max_length=50, null=True, blank=True)

    # admin's permission -->
    t_approval = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.t_name} Teacher"
    
    class Meta:
        verbose_name_plural = "ALL TEACHERS"


class_for_student = [
    ('one', 'one'),
    ('two', 'two'),
    ('three', 'three'),
    ('four', 'four'),
    ('five', 'five'),
    ('six', 'six'),
    ('seven', 'seven'),
    ('eight', 'eight'),
    ('nine_science', 'nine_science'),
    ('nine_commerce', 'nine_commerce'),
    ('nine_arts', 'nine_arts'),
    ('ten_science', 'ten_science'),
    ('ten_commerce', 'ten_commerce'),
    ('ten_arts', 'ten_arts'),
    ('inter_first_year_science', 'inter_first_year_science'),
    ('inter_first_year_commerce', 'inter_first_year_commerce'),
    ('inter_first_year_arts', 'inter_first_year_arts'),
    ('inter_second_year_science', 'inter_second_year_science'),
    ('inter_second_year_commerce', 'inter_second_year_commerce'),
    ('inter_second_year_arts', 'inter_second_year_arts'),
    
]

class Subjects(models.Model):
    name = models.CharField(max_length=100 )

    def __str__(self):
        return self.name
    
class SubjectsPerClass(models.Model):
    s_class = models.CharField(max_length=50, choices=class_for_student, null=True, blank=True)
    subjects = models.ManyToManyField(Subjects)

    def __str__(self):
        return self.s_class
    


class Shift(models.Model):

    shift_name = models.CharField( max_length=50)

    
    def __str__(self):
        return f"{self.shift_name}"

class Batch(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    batch_name = models.CharField( max_length=50)
    class_start = models.TimeField( auto_now=False, auto_now_add=False,null=True,blank=True)
    class_end = models.TimeField( auto_now=False, auto_now_add=False,null=True,blank=True)
    max_seat = models.IntegerField(default=35)
    total_available_seats = models.IntegerField(default=35, null=True, blank=True)

    def __str__(self):
        return f"{self.batch_name} - Available Seats - {self.total_available_seats}"




# HERE need to change for not allow to enter new timw within first class duration (Need UPDATE) -->
class MakeBatch(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    class_name = models.ForeignKey( SubjectsPerClass, on_delete=models.CASCADE)

    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, null=True,blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True,blank=True)
    start_class = models.TimeField(null=True,blank=True)
    end_class = models.TimeField(null=True, blank=True)
   

    # def save(self, *args, **kwargs):
    #     if self.class_name:
            
    #         choices = [(subject.name, subject.name) for subject in self.class_name.subjects.all()]
    #         self._meta.get_field('subject').choices = choices
       
    #     super().save(*args, **kwargs)


    def __str__(self):
        return f"BATCH : {self.batch} - {self.class_name} - {self.subject} - {self.teacher}"
    
    
 
class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    # ADMINS permission -->
    basic_step_of_reg = models.BooleanField(default=False)
    choose_subjects = models.BooleanField(default=False)
    s_approval = models.BooleanField(default=False)
    guardian_phone_is_verified = models.BooleanField(default=False)

    # Basic information
    s_name = models.CharField(max_length=170, null=True, blank=True) 
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, null=True, blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True)
    profile_pic = models.ImageField( upload_to="student", default='avatar.png')

    # mandatory
    class_subjects = models.ForeignKey(SubjectsPerClass, on_delete=models.CASCADE, null=True, blank=True )
    s_id = models.IntegerField(null=True, blank=True)
    guardian_phone = models.CharField(max_length=15)
    your_subjects = MultiSelectField(max_length=170, null=True, blank=True)
    
    # Optional fields
    s_phone = models.CharField(max_length=15, blank=True, null=True)
    guardian_email = models.EmailField(max_length=100, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __init__(self, *args, **kwargs):
        super(Student, self).__init__(*args, **kwargs)

        if self.class_subjects:
            self._meta.get_field('your_subjects').choices = [
                (subject.name.lower(), subject.name) for subject in self.class_subjects.subjects.all()
            ]

        else:
            self._meta.get_field('your_subjects').choices = [
                ('math', 'math')
            ]
    def calculate_total_students(self):
        if self.batch:
            return Student.objects.filter(batch=self.batch).count()
        else:
            return 0

    def save(self, *args, **kwargs):
        super(Student, self).save(*args, **kwargs)

        # Check if a batch is assigned to the student and update available seats
        if self.batch:
            self.batch.total_available_seats = self.batch.max_seat - self.calculate_total_students()
            self.batch.save()
            
    def __str__(self):
        if self.s_name:
            return self.s_name
        else:
            return f"STUDENT ID - {self.s_id}"
        

    class Meta:
        verbose_name_plural = "ALL STUDENTS"

class Guardian(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    basic_step_of_reg = models.BooleanField(default=False)
    
    
    # BASICS
    g_name = models.CharField(max_length=100)
    children = models.ManyToManyField(Student)
    present_adress = models.CharField( max_length=150,blank=True, null=True)
    extra_phone_no = models.CharField( max_length=50, blank=True, null=True)

    # admin's permission -->
    g_approval = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "ALL GUARDIANS"

 
class CreateExam(models.Model):
    exam_name = models.CharField(max_length=150)
    out_of = models.IntegerField(default=100)

    def __str__(self):
        return self.exam_name

class MarksOfStudent(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    std = models.ForeignKey(Student, on_delete=models.CASCADE)
    student_id = models.IntegerField()  # Renamed the field to student_id
    subject = models.CharField(max_length=150)
    exam_type = models.ForeignKey(CreateExam, null=True, blank=True, on_delete=models.CASCADE)
    mark = models.IntegerField()

    def __str__(self):
        return f"{self.std} - {self.subject}"



# Try to collect fee accourding to student's ability per month.

# class FeesForScienceStudent(models.Model):
#     physics = models.IntegerField()
#     chemistry = models.IntegerField()
#     biology = models.IntegerField()
#     higher_math = models.IntegerField()


# class FeePerStudent(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     grand_total_fee = models.IntegerField(null=True, blank=True)