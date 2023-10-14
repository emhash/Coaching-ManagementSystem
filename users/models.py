from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomManager
from multiselectfield import MultiSelectField
from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import uuid


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


    class Meta:
        verbose_name_plural = "ইউজার অ্যাকাউন্ট *VIP* "

 
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
        verbose_name_plural = "ইউজার( শিক্ষক-শিক্ষিকা )"


class_for_student = [
    ('প্রথম', 'প্রথম'),
    ('দ্বিতীয়', 'দ্বিতীয়'),
    ('তৃতীয়', 'তৃতীয়'),
    ('চতুর্থ', 'চতুর্থ'),
    ('পঞ্চম', 'পঞ্চম'),
    ('ষষ্ঠ', 'ষষ্ঠ'),
    ('সপ্তম', 'সপ্তম'),
    ('অস্টম', 'অস্টম'),
    ('নবম(বিজ্ঞান)', 'নবম(বিজ্ঞান)'),
    ('নবম(ব্যাবসায় শিক্ষা)', 'নবম(ব্যাবসায় শিক্ষা)'),
    ('নবম(মানবিক)', 'নবম(মানবিক)'),
    ('দশম(বিজ্ঞান)', 'দশম(বিজ্ঞান)'),
    ('দশম(ব্যাবসায় শিক্ষা)', 'দশম(ব্যাবসায় শিক্ষা)'),
    ('দশম(মানবিক)', 'দশম(মানবিক)'),
    ('একাদশ (বিজ্ঞান)', 'একাদশ (বিজ্ঞান)'),
    ('একাদশ (ব্যাবসায় শিক্ষা)', 'একাদশ (ব্যাবসায় শিক্ষা)'),
    ('একাদশ (মানবিক)', 'একাদশ (মানবিক)'),
    ('দাদশ (বিজ্ঞান)', 'দাদশ (বিজ্ঞান)'),
    ('দাদশ (ব্যাবসায় শিক্ষা)', 'দাদশ (ব্যাবসায় শিক্ষা) '),
    ('দাদশ (মানবিক)', 'দাদশ (মানবিক)'),
    
]

class Subjects(models.Model):
    name = models.CharField(max_length=100 )

    def __str__(self):
        return self.name
    

    class Meta:
        verbose_name_plural = "বিষয় যুক্ত করুন"


class ClassWithSubject(models.Model):
    s_class = models.CharField(max_length=50, choices=class_for_student, null=True, blank=True)
    subjects = models.ManyToManyField(Subjects)

    def __str__(self):
        return self.s_class
    

    class Meta:
        verbose_name_plural = "শ্রেণী হিসেবে বিষয় নির্বাচন"


class Shift(models.Model):
    shift_name = models.CharField( max_length=50)

    def __str__(self):
        return f"{self.shift_name}"


    class Meta:
        verbose_name_plural = "শিফট তৈরি"


class Batch(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    batch_name = models.CharField( max_length=50)
    class_start = models.TimeField( auto_now=False, auto_now_add=False,null=True,blank=True)
    class_end = models.TimeField( auto_now=False, auto_now_add=False,null=True,blank=True)
    max_seat = models.IntegerField(default=35)
    total_available_seats = models.IntegerField(default=35, null=True, blank=True)

    def __str__(self):
        return f"{self.batch_name} - খালি আসন- {self.total_available_seats}"


    class Meta:
        verbose_name_plural = "ব্যাচ তৈরি"



# HERE need to change for not allow to enter new timw within first class duration (Need UPDATE) -->

class MakeBatch(models.Model):


    # DAY_CHOICES = (
    #     ('Saturday', 'Saturday'),
    #     ('Sunday', 'Sunday'),
    #     ('Monday', 'Monday'),
    #     ('Tuesday', 'Tuesday'),
    #     ('Wednesday', 'Wednesday'),
    #     ('Thursday', 'Thursday'),
    #     ('Friday', 'Friday'),
    # )


    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    class_name = models.ForeignKey( ClassWithSubject, on_delete=models.CASCADE)

    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, null=True,blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True,blank=True)
    start_class = models.TimeField(null=True,blank=True)
    end_class = models.TimeField(null=True, blank=True)
    # day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES, null=True, blank=True)
   

    # def save(self, *args, **kwargs):
    #     if self.class_name:
            
    #         choices = [(subject.name, subject.name) for subject in self.class_name.subjects.all()]
    #         self._meta.get_field('subject').choices = choices
       
    #     super().save(*args, **kwargs)


    def __str__(self):
        return f"BATCH : {self.batch} - {self.class_name} - {self.subject} - {self.teacher}"
    

    class Meta:
        verbose_name_plural = "ব্যাচ ও বিষয় ভিত্তিক শিক্ষক"

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
    class_subjects = models.ForeignKey(ClassWithSubject, on_delete=models.CASCADE, null=True, blank=True )
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
        verbose_name_plural = "ইউজার ( শিক্ষার্থী )"

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
        verbose_name_plural = "ইউজার ( অভিভাবক )"

 
class CreateExam(models.Model):
    exam_name = models.CharField(max_length=150)
    out_of = models.IntegerField(default=100)

    def __str__(self):
        return self.exam_name

    class Meta:
        verbose_name_plural = "পরীক্ষা তৈরি করুন"



class MarksOfStudent(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    std = models.ForeignKey(Student, on_delete=models.CASCADE)
    student_id = models.IntegerField()  
    subject = models.CharField(max_length=150)
    exam_type = models.ForeignKey(CreateExam, null=True, blank=True, on_delete=models.CASCADE)
    mark = models.IntegerField()

    def __str__(self):
        return f"{self.std} - {self.subject}"


    class Meta:
        verbose_name_plural = "শিক্ষার্থীদের মার্কস"



class MessageForTeacher(models.Model):

    headline = models.CharField( max_length=250)
    description = RichTextField(blank=True, null=True)
    message_for = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    upload_at = models.DateTimeField(auto_now_add=True)
    visited = models.BooleanField()
    

    def __str__(self) -> str:
        return self.headline

    class Meta:
        verbose_name_plural = "শিক্ষকদের বার্তা পাঠান"


class MessageForStudent(models.Model):

    headline = models.CharField( max_length=250)
    description = RichTextField(blank=True, null=True)
    message_for = models.ForeignKey(Student, on_delete=models.CASCADE)
    upload_at = models.DateTimeField(auto_now_add=True)
    visited = models.BooleanField()


    def __str__(self) -> str:
        return self.headline
 
    class Meta:
        verbose_name_plural = "শিক্ষার্থীদের বার্তা পাঠান"


class NoteAndSheet(models.Model):
    title = models.CharField( max_length= 150)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    for_class = models.ForeignKey(ClassWithSubject, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    upload_note = models.FileField(upload_to="notes", default='coaching.pdf',null=True,blank=True)

    class Meta:
        verbose_name_plural = "শিক্ষকদের দেওয়া নোট"



class HomeWork(models.Model):
    title = models.CharField( max_length= 150)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    hw_detail = RichTextField()
    last_day_of_submit = models.DateField( auto_now=False, auto_now_add=False)
    for_class = models.ForeignKey(ClassWithSubject, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "শিক্ষকদের দেওয়া বাড়িরকাজ"

    def __str__(self):
        return self.title

# base model , that data are common for others model also. 
class CommonBaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default= uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# inheriting my common base model that are common in this model also
class QuizCategory(CommonBaseModel):
    name = models.CharField( max_length=90)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE,null=True,blank=True)
    class_name = models.ForeignKey(ClassWithSubject, on_delete=models.CASCADE,null=True,blank=True)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE,null=True,blank=True)
    duration = models.IntegerField(default=5)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name_plural = "কুইজ এর ধরন তৈরি"


class Question(CommonBaseModel):
    category = models.ForeignKey(QuizCategory,related_name='category', on_delete=models.CASCADE)
    ques_name = models.CharField( max_length=90)
    mark = models.IntegerField(default=1)
    how_many_answer_for_this_ques = models.IntegerField(default=4)

    def __str__(self):
        return self.ques_name

    class Meta:
        verbose_name_plural = "কইজ প্রশ্ন তৈরি"



class Answer(CommonBaseModel):
    answer = models.CharField( max_length=150)
    qustion = models.ForeignKey(Question, related_name='question', on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer
    
    class Meta:
        verbose_name_plural = "কইজ উত্তর তৈরি"

class ApplyForLeave(CommonBaseModel):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    reason_for_apply = models.CharField( max_length=250)
    description = models.TextField()
    attachment = models.FileField( upload_to="tacher_reasons")

    def __str__(self) -> str:
        return f" {self.teacher} - {self.created_at} "
    

class NoticeForStudent(CommonBaseModel):
    notice = models.CharField( max_length=250)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    notice_last_for = models.DateField(auto_now=False, auto_now_add=False)
    
    def __str__(self) -> str:
        return f"To {self.student} : {self.notice} " 
    

class StudetFeedback(models.Model):
    already_rated = models.BooleanField(default=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    rate_us = models.IntegerField( null=True, blank=True)
    report = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.student} rates {self.rate_us}"


class ExamSchedule(models.Model):
    name = models.CharField( max_length=150)
    file = models.FileField( upload_to="xm_schedule")
    batch = models.ForeignKey( Batch, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

