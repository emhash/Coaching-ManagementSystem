from django.contrib import admin
from .models import CustomUser, Student, Teacher, Guardian, ClassWithSubject,Subjects,Shift,Batch,MakeBatch,MarksOfStudent,CreateExam,MessageForTeacher,MessageForStudent

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone_number', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'phone_number')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 't_name', 'teacher_background', 't_approval', 'created_at')
    list_filter = ('teacher_background', 't_approval', 'created_at')
    search_fields = ('user__email', 't_name')

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('user', 'g_name', 'g_approval', 'created_at')
    list_filter = ('g_approval', 'created_at')
    search_fields = ('user__email', 'g_name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 's_name', 'class_subjects', 's_approval', 'batch', 'guardian_phone_is_verified')
    list_filter = ('class_subjects', 's_approval', 'guardian_phone_is_verified', 'created_at','batch')
    search_fields = ('user__email', 's_name', 's_id', 'guardian_phone')

class ClassWithSubjects(admin.ModelAdmin):
    filter_horizontal = ('subjects',)
    # list_display = ('id',)

admin.site.register(ClassWithSubject, ClassWithSubjects)



  
# @admin.register(CreateShift)
# class CreateShiftAdmin(admin.ModelAdmin):
#     list_display = ('id','shift_name_of_class','the_class','teacher')
    
admin.site.register(Subjects)

admin.site.register(Shift)

admin.site.register(Batch)
  

class MakeBatchAdmin(admin.ModelAdmin):
    list_display = ('batch', 'class_name', 'subject', 'teacher')
    list_filter = ('class_name', 'teacher')
    search_fields = ('batch__name', 'class_name__s_class', 'subject', 'teacher__name')
    list_per_page = 20

admin.site.register(MakeBatch, MakeBatchAdmin)

class MarksOfStudentAdmin(admin.ModelAdmin):
    list_display = ('batch', 'subject', 'std', 'mark')  
    list_filter = ('batch', 'mark')  

    list_per_page = 20

admin.site.register(MarksOfStudent, MarksOfStudentAdmin)

admin.site.register(CreateExam)
admin.site.register(MessageForTeacher)
admin.site.register(MessageForStudent)