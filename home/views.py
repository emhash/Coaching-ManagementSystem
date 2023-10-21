from .forms import ApplyLeaveForm, TeacherProfileForm,PassChangeForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect,get_object_or_404, HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, logout, login
from .forms import CommonRegistrationForm, StudentForm, TeacherForm,StudentEditForm,NoteAndSheetForm,NoteAndSheetForm,HomeWorkForm,QuestionForm,AnswerForm
from datetime import datetime
from users.models import *
from .more_backend import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os
from django.http import StreamingHttpResponse 
from wsgiref.util import FileWrapper
import mimetypes


def home(request):  
    if request.user.is_authenticated:
        return redirect('authentication')
    else:
        return render(request, 'main/index.html')

@login_required
def logout_view(request):
    logout(request)

    return redirect('home')

def userlogin(request):
    
    if request.user.is_authenticated :
        redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  
        else:
            messages.error(request, "Your provided data is not valid")
    return render(request, 'main/login.html')

def register_role(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        request.session['selected_role'] = role
        return redirect('registration')
        
    return render(request, 'registration/choose_role.html')

def registration(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        role = request.session.get('selected_role')
        if role:
            form = CommonRegistrationForm(request.POST or None)
            context = {
                'form': form,
                'role' : role,
            }
            if form.is_valid():

                user = form.save(commit=False)
                user.role = role
                user.save()
                
                if role == 'student':
                        user_profile = Student(user=user)
                elif role == 'teacher':
                    user_profile = Teacher(user=user)
                elif role == 'guardian':
                    user_profile = Guardian(user=user)
                else:
                    # Handle unsupported role or not essigned
                    redirect('register_role')

                user_profile.save()
                login(request, user)  
                return redirect('home')
            
            return render(request, 'main/registration.html', context)
        else:
            return redirect('register_role')
    
@login_required
def authentication(request):
    if request.user.role == 'student':
        student_profile = Student.objects.get(user=request.user)
        if student_profile.basic_step_of_reg:
            if student_profile.choose_subjects:
                return render(request, 'main/index.html' , {'student_profile' : student_profile})
            else:
                if request.method == 'POST':
                    selected_subjects = request.POST.getlist('selected_subjects')
                    # print("Selected subjects:", selected_subjects)  
                    student_profile.your_subjects = selected_subjects 
                    student_profile.choose_subjects = True
                    
                    student_profile.save()
                    return render(request, 'main/index.html')
                else:
                    return render(request, 'home/choose_subjects.html', {'student_profile': student_profile})
        else:
            student_profile = Student.objects.get(user=request.user)
            if request.method == 'POST':
                form = StudentForm(request.POST, instance=student_profile)
                if form.is_valid():
                    student_profile.basic_step_of_reg = True
                    student_profile.s_id = generate_unique_integer_id() 
                    form.save()
                    return redirect('home')
            else:
                form = StudentForm(instance=student_profile)
            return render(request, 'registration/register_student.html', {'form': form})  

    elif request.user.role == 'teacher':
        teacher_profile = Teacher.objects.get(user=request.user)
        if teacher_profile.basic_step_of_reg:
            return render(request, 'main/index.html')
        else:
            teacher_profile = Teacher.objects.get(user=request.user)
            if request.method == 'POST':
                form = TeacherForm(request.POST, instance=teacher_profile)
                if form.is_valid():
                    teacher_profile.basic_step_of_reg = True
                    # teacher_profile.s_id = f"T{generate_unique_integer_id()}"
                    form.save()
                    return redirect('home')
            else:
                form = TeacherForm(instance=teacher_profile)
            return render(request, 'registration/register_teacher.html' , {'form' : form})
        
    elif request.user.role == 'guardian':
        guardian_profile = Guardian.objects.get(user=request.user)

        if guardian_profile.basic_step_of_reg:        
            return render(request, 'main/index.html')
        else:
            return render(request, 'registration/register_guardian.html')
    else:
        return render(request, 'main/404.html')


@login_required
def student_dashb(request, page=None):
    if request.user.role == 'student':

        if page == 'feedback':
            student = request.user.student
            feedback, created = StudetFeedback.objects.get_or_create(student=student, defaults={
                'already_rated': False,
                'rate_us': 0,
                'report': ''
            })

            if request.method == "POST":
                try:
                    feedback.already_rated = True
                    feedback.rate_us = request.POST.get('star_rating')
                    feedback.report = request.POST.get('speech')
                    feedback.save()
                    return redirect('student_dashb', page='feedback')
                except Exception as e:
                    return render(request, 'student/error.html', {"error_message": e})

            context = {
                'data': feedback,
            }
            return render(request, 'student/dash_feedback.html', context)

        elif page == 'message':
            all_msg = MessageForStudent.objects.filter(message_for = request.user.student).order_by('-upload_at', 'visited')
            
            context = {
                'all_message':all_msg,
            }

            return render(request, 'student/dash_message.html', context)
        elif page == 'settings':
            return edit_profile(request)
   
        elif page == 'hw':
            
            std = Student.objects.get(user=request.user)
            std_cls_id = std.class_subjects.id
            std_batch_id = std.batch.id
            selected_subjects = std.your_subjects
            sheet = []

            for s in selected_subjects:
                queryset = HomeWork.objects.filter(
                    for_class__id=std_cls_id,
                    batch=std_batch_id,
                    subject__name=s,
                )
                
                if queryset.exists():
                    sheet.append(queryset)

            context = {'hw': sheet}
            return render(request, 'student/hw.html', context)
        
        elif page == 'sheet':
            
            std = Student.objects.get(user=request.user)
            std_cls_id = std.class_subjects.id
            std_batch_id = std.batch.id
            selected_subjects = std.your_subjects
            sheet = []

            for s in selected_subjects:
                queryset = NoteAndSheet.objects.filter(
                    for_class__id=std_cls_id,
                    batch=std_batch_id,
                    subject__name=s,
                )
                
                if queryset.exists():
                    sheet.append(queryset)

            context = {'note': sheet}
            return render(request, 'student/sheets.html', context)

        elif page == 'routine':

            student = request.user.student
            routine = []

            # student's batch
            student_batch = student.batch

            if student_batch:
                # the subjects for the student's class
                subjects_per_class = student.class_subjects

                if subjects_per_class:
                    # the subjects related to the student's class
                    subjects = subjects_per_class.subjects.all()

                    # For each subject, get the routine data
                    for subject in subjects:
                        # Filter MakeBatch objects based on both batch and class
                        data = MakeBatch.objects.filter(batch=student_batch, class_name=subjects_per_class, subject=subject)
                        # print(data)
                        if data:
                            routine.append(data)
                    # print(routine)

            context = {'routine': routine}
            return render(request, 'student/routine.html', context)

        elif page == 'class':

            student = request.user.student
            routine = []

            # student's batch
            student_batch = student.batch

            if student_batch:
                # the subjects for the student's class
                subjects_per_class = student.class_subjects

                if subjects_per_class:
                    # the subjects related to the student's class
                    subjects = subjects_per_class.subjects.all()

                    # For each subject, get the routine data
                    for subject in subjects:
                        # Filter MakeBatch objects based on both batch and class
                        data = MakeBatch.objects.filter(batch=student_batch, class_name=subjects_per_class, subject=subject)
                        # print(data)
                        if data:
                            routine.append(data)
                    # print(routine)

            context = {'routine': routine}
            return render(request, 'student/dash_class.html', context)

        elif page == 'change_password':
            return change_password(request)
        
        elif page == 'mark':
            exam_id = request.GET.get('exam_id')  
            # print(exam_id)
            exam = CreateExam.objects.all()
            # marks = MarksOfStudent.objects.filter(exam_type=exam_id)
            marks =[]

            if exam_id:
                marks = MarksOfStudent.objects.filter(exam_type=exam_id, student_id = request.user.student.s_id)
                for m in marks:
                    the_grade = calculate_grade(m.mark, m.exam_type.out_of)
                    m.the_grade = the_grade

            return render(request, 'student/res.html', {'exam': exam, 'marks': marks})

        elif page == 'result':
            # print(request.user.student)
            mark = MarksOfStudent.objects.filter(student_id = request.user.student.s_id)
            # for m in mark:
            #     print(m.mark)
            
            return render(request, 'student/dash_result.html', context={'marks':mark})

        elif page == 'xm_schedule':
            

            schedule = ExamSchedule.objects.filter(batch__student = request.user.student)
            # print(schedule)

            context={
                'schedule':schedule,
            }
            return render(request, 'student/xm_schedule.html', context)

        else:
            std = Student.objects.get(user=request.user)
            std_cls_id = std.class_subjects.id
            std_batch_id = std.batch.id
            selected_subjects = std.your_subjects
            sheet = []

            for s in selected_subjects:
                queryset = HomeWork.objects.filter(
                    for_class__id=std_cls_id,
                    batch=std_batch_id,
                    subject__name=s,
                )
                if queryset.exists():
                    sheet.append(queryset)

            
            current_date = datetime.now().date()
            one_day_ahead = current_date + timedelta(days=1)
            
            
            reminders = []
            for s in sheet:
                for d in s:
                    if d.last_day_of_submit == one_day_ahead:
                        reminders.append(s)

            notiss = NoticeForStudent.objects.filter(student=std)
            notice =[]
            
            
            for nts in notiss:
                two_day_back= nts.notice_last_for + timedelta(days=-2)
                if two_day_back <= current_date and current_date <= nts.notice_last_for:

                    notice.append(nts)
                    


            context = {
                'reminders': reminders,
                'notice': notice,
                       
                       }
            return render(request, 'student/dash_home.html', context)
    
    
    else:
        return render(request, 'main/404.html')
    

# =--------------------STUDENT DAHBOARD ADITIONAL SETTINGS-----------------------------==
@login_required
def view_hw(request, hw_id):

    detail_hw = get_object_or_404(HomeWork, id = hw_id, )
    
    context = {
        'detail_hw':detail_hw,
    }
    return render(request, 'student/view_hw.html', context)

# =-------------------------------------------------==


# ----------------------------------- DONE (working on add marks) ------------------------------------------------
@login_required
def add_mark1(request, shift):
    try:
        
        sft = Shift.objects.get(shift_name=shift)
        the_batch = Batch.objects.get(shift=sft)
        ts = Teacher.objects.get(user=request.user)
        data = MakeBatch.objects.filter(batch=the_batch, teacher=ts)
        dls = set()
        for d in data:
            shft = get_object_or_404(ClassWithSubject, s_class=d.class_name)
            dls.add(shft)

        # print(dls)
        # current_user_teacher = Teacher.objects.get(user=request.user)
        # # Query the MakeBatch objects related to the selected Shift and teacher
        # make_batches = MakeBatch.objects.filter(batch__shift=shft, teacher=current_user_teacher)

        return render(request, 'teacher/add_mark1.html', {'data': dls, 'shift': shift})

    except (Shift.DoesNotExist, Batch.DoesNotExist, Teacher.DoesNotExist) as e:
        return render(request, 'teacher/error.html', {'error_message': 'সিস্টেম এর ত্রুটি ! আপনি যে তথ্য এর রিকুয়েস্ট দিয়েছেন তা হয়ত সিস্টেমে নেই অথবা এই ফাংসন সংযুক্ত করা হয়নি। '})

    except Exception as e:
        return render(request, 'teacher/error.html', {'error_message': str(e)})

@login_required
def add_mark2(request, shift, cls):
    try:
        sft = get_object_or_404(Shift, shift_name=shift)
        the_batch = get_object_or_404(Batch, shift=sft)
        ts = Teacher.objects.get(user=request.user)
        data = MakeBatch.objects.filter(batch=the_batch, teacher=ts, class_name=cls)

        return render(request, 'teacher/add_mark2.html', {'data': data, 'shift': shift, 'c_id': cls})

    except (Shift.DoesNotExist, Batch.DoesNotExist, Teacher.DoesNotExist) as e:
        return render(request, 'teacher/error.html', {'error_message': 'One or more objects not found.'})

    except Exception as e:
        return render(request, 'teacher/error.html', {'error_message': str(e)})

@login_required
def add_mark3(request, shift, cls, subject):
    try:
        sft = get_object_or_404(Shift, shift_name=shift)
        the_batch = get_object_or_404(Batch, shift=sft)
        subj = get_object_or_404(Subjects, name=subject)

        ts = Teacher.objects.get(user=request.user)
        data = MakeBatch.objects.filter(batch=the_batch, teacher=ts, class_name=cls)

        students = []

        for d in data:
            # Filtering students according to the current batch
            batch_students = Student.objects.filter(batch_id=d.batch.id, your_subjects__contains=subj.name, class_subjects=cls)
            students.extend(batch_students)

        exam = CreateExam.objects.all()

        return render(request, 'teacher/add_mark3.html', {'students': students, 'exam': exam, 'shift': shift, 'cls': cls, 'subject': subject})

    except (Shift.DoesNotExist, Batch.DoesNotExist, Subjects.DoesNotExist, Teacher.DoesNotExist) as e:
        return render(request, 'teacher/error.html', {'error_message': 'One or more objects not found.'})

    except Exception as e:
        return render(request, 'teacher/error.html', {'error_message': str(e)})

@login_required
def add_mark4(request, shift, cls, subject, exam):
    try:
        sft = get_object_or_404(Shift, shift_name=shift)
        the_batch = get_object_or_404(Batch, shift=sft)
        subj = get_object_or_404(Subjects, name=subject)

        ts = Teacher.objects.get(user=request.user)
        data = MakeBatch.objects.filter(batch=the_batch, teacher=ts, class_name=cls)
        marks_dict = {}
      
        for d in data:
            batch_students = Student.objects.filter(batch_id=d.batch.id, your_subjects__contains=subj.name, class_subjects=cls)
            
            for student in batch_students:
                try:
                    the_exam = CreateExam.objects.get(exam_name=exam)  
                    mark = MarksOfStudent.objects.get(batch=the_batch, std=student, subject=subject, exam_type=the_exam)
                    the_mark = mark.mark
                    
                    the_grade = calculate_grade(mark.mark, the_exam.out_of)

                    marks_dict[student.s_id] = [the_mark, the_grade]
                except MarksOfStudent.DoesNotExist:
                    marks_dict[student.s_id] = [None, None]
                
                # With this, we can assign a new temp field to a query set. so now we can use 'student.marking'
                student.marking = marks_dict

        if request.method == "POST":
            std_mark = request.POST.get('marks')
            std_id = request.POST.get('sid')
            std_name = request.POST.get('s_name')

            the_student = Student.objects.get(batch_id=d.batch.id, s_id=std_id, your_subjects__contains=subj.name, class_subjects=cls)
            the_exam = CreateExam.objects.get(exam_name=exam)

            # Check if marks already exist for the student and exam
            try:
                mark_table = MarksOfStudent.objects.get(batch=the_batch, std=the_student, subject=subject, exam_type=the_exam)
                mark_table.mark = std_mark

            except MarksOfStudent.DoesNotExist:
                mark_table = MarksOfStudent.objects.create(batch=the_batch, std=the_student, student_id=std_id, subject=subject, exam_type=the_exam, mark=std_mark)
            
            mark_table.save()
            return redirect('add_mark4', shift=shift, cls=cls, subject=subject, exam=exam)

        return render(request, 'teacher/add_mark4.html', {'students': batch_students, 'mark_dict': marks_dict })

    except (Shift.DoesNotExist, Batch.DoesNotExist, Subjects.DoesNotExist, Teacher.DoesNotExist) as e:
        return render(request, 'teacher/error.html', {'error_message': 'One or more objects not found.'})

    except Exception as e:
        return render(request, 'teacher/error.html', {'error_message': str(e)})



# ----------------------------------------------------------------------------------


@login_required
def teacher_dashb(request, page=None):
    if request.user.role == 'teacher':
        if page == 'add_mark':
            shift = Shift.objects.all()

            return render(request, 'teacher/add_mark.html', {'data':shift})
        
        elif page == 'msg':
            all_msg = MessageForTeacher.objects.filter(message_for = request.user.teacher).order_by('upload_at', '-visited')
            
            context = {
                'all_message':all_msg,
            }
            return render(request, 'teacher/msg.html', context)
        
        elif page == 'apply_leave':
            if request.method == "POST":
                form = ApplyLeaveForm(request.POST, request.FILES)
                try:
                    if form.is_valid():
                        form.save(commit=False)
                        form.instance.teacher = request.user.teacher
                        form.save()
                        messages.success(request, "Congrats! Your application has been submitted to the admin.")
                        return redirect('teacher_dashb', page='home')
                except Exception as e:
                    return render(request, 'teacher/error.html', {'error_message': e})
            else:
                form = ApplyLeaveForm()
            context = {
                'form' : form, 
            }
            return render(request, 'teacher/apply_leave.html', context)
        
        elif page == 'all_setting':
            return redirect('edit_profile')
        
        elif page == 'hw':

            current_teacher = request.user.teacher  
            make_batch_objects = MakeBatch.objects.filter(teacher=current_teacher)
            notes = HomeWork.objects.filter(teacher = current_teacher)
            
            if request.method == 'POST':
                form = HomeWorkForm(request.POST, request.FILES)
                try:
                    if form.is_valid():
                        form.instance.teacher = request.user.teacher
                        form.save()

                        messages.success(request, f"আপনি সফল ভাবে ক্লাস {form.cleaned_data['for_class']} এর ব্যাচ {form.cleaned_data['batch']} এ বাড়ির কাজ প্রদান করেছেন। ")
                        return redirect('teacher_dashb', page='hw')
                except:
                    
                    return render(request, 'teacher/error.html', {'error_message': form.errors})
            else:
                
                form = HomeWorkForm()

                # Get distinct batches, classes, and subjects based on MakeBatch objects
                distinct_batches = make_batch_objects.values('batch_id', 'batch__batch_name').distinct()
                distinct_classes = make_batch_objects.values('class_name_id', 'class_name__s_class').distinct()
                distinct_subjects = make_batch_objects.values('subject_id', 'subject__name').distinct()
                
                form.fields['batch'].choices = [('', 'Select Batch')] + [(batch['batch_id'], batch['batch__batch_name']) for batch in distinct_batches]
                form.fields['for_class'].choices = [('', 'Select Class')] + [(class_item['class_name_id'], class_item['class_name__s_class']) for class_item in distinct_classes]
                form.fields['subject'].choices = [('', 'Select Subject')] + [(subject['subject_id'], subject['subject__name']) for subject in distinct_subjects]
            
            context = {
                'subs': notes,
                'form' : form
            }

            return render(request, 'teacher/hw.html', context)
        
        elif page == 'quiz':
            teacher = request.user.teacher
            # reverse example of database from subject to makebatch class's teacher filter
            subjects = Subjects.objects.filter(makebatch__teacher=teacher)
            # applying distinct() to ensure that duplicate rows are removed
            the_class = ClassWithSubject.objects.filter(makebatch__teacher=teacher).distinct()
    

            if request.method == 'POST':
                the_title = request.POST.get('heading') 
                selected_subject_id = request.POST.get('subject')
                selected_class_id = request.POST.get('classes')
                # Get the start_from value from the form
                start_from_str = request.POST.get('start_from')
                print(start_from_str)
                # Correct format for datetime-local input
                start_from = datetime.strptime(start_from_str, '%Y-%m-%dT%H:%M')
    
                # Create a QuizCategory instance and set its fields
                quiz_category = QuizCategory()
                quiz_category.name = the_title
                quiz_category.teacher = teacher
                quiz_category.class_name_id = selected_class_id
                quiz_category.subject_id = selected_subject_id
                quiz_category.duration = request.POST.get('duration')
                quiz_category.start_from = start_from
                try:
                    quiz_category.save()
                    messages.success(request, "Congrats! কইজ এর তালিকা ও ক্যাটাগরি যুক্ত করা হয়েছে ")
                    return redirect('teacher_dashb', page='quiz')
                except Exception as e:
                    return render(request, 'teacher/error.html', {'error_message': e})

            quizz = QuizCategory.objects.filter(teacher = teacher)
            # print(quizz)
            data={
                'subject':subjects,
                'classes':the_class,
                'quizes':quizz,
            }
            return render(request, 'teacher/quiz.html', context=data)
        
        elif page == 'your_student':
            batch_of_teacher = MakeBatch.objects.filter(teacher = request.user.teacher)
            
            your_students = set()

            for b in batch_of_teacher:
                subj = get_object_or_404(Subjects, name=b.subject)
                cls = get_object_or_404(ClassWithSubject, s_class=b.class_name)
                the_student = Student.objects.filter(batch_id=b.batch.id, 
                                                     your_subjects__contains=subj.name, 
                                                     class_subjects=cls
                                                    ).order_by('created_at')
                
                for s in the_student:
                    # print(s.created_at)
                    your_students.add(s)

            # print(your_students)
            
            return render(request, 'teacher/your_student.html', {'students':your_students})
        
        elif page == 'wallet':
            return render(request, 'teacher/wallet.html')
        
        elif page == 'routine':
            routine = MakeBatch.objects.filter(teacher = request.user.teacher)
            return render(request, 'teacher/routine.html', {'routine':routine})
        
        elif page == 'your_subject':
            sub = MakeBatch.objects.filter(teacher = request.user.teacher)
            return render(request, 'teacher/your_subject.html', {'subs':sub})


        elif page == 'note':
            current_teacher = request.user.teacher  
            make_batch_objects = MakeBatch.objects.filter(teacher=current_teacher).distinct()
            notes = NoteAndSheet.objects.filter(teacher = current_teacher)
            
            if request.method == 'POST':
                form = NoteAndSheetForm(request.POST, request.FILES)
                try:
                    if form.is_valid():
                        form.instance.teacher = request.user.teacher
                        form.save()

                        messages.success(request, f"আপনি সফল ভাবে ক্লাস {form.cleaned_data['for_class']} এর ব্যাচ {form.cleaned_data['batch']} এ বাড়ির কাজ প্রদান করেছেন। ")
                        return redirect('teacher_dashb', page='note')
                except:
                    
                    return render(request, 'teacher/error.html', {'error_message': form.errors})
            else:
                form = NoteAndSheetForm()
                # Get distinct batches, classes, and subjects based on MakeBatch objects
                distinct_batches = make_batch_objects.values('batch_id', 'batch__batch_name').distinct()
                distinct_classes = make_batch_objects.values('class_name_id', 'class_name__s_class').distinct()
                distinct_subjects = make_batch_objects.values('subject_id', 'subject__name').distinct()
                
                form.fields['batch'].choices = [('', 'Select Batch')] + [(batch['batch_id'], batch['batch__batch_name']) for batch in distinct_batches]
                form.fields['for_class'].choices = [('', 'Select Class')] + [(class_item['class_name_id'], class_item['class_name__s_class']) for class_item in distinct_classes]
                form.fields['subject'].choices = [('', 'Select Subject')] + [(subject['subject_id'], subject['subject__name']) for subject in distinct_subjects]
         
            context = {
                'subs': notes,
                'form' : form
            }
            return render(request, 'teacher/note.html', context)
        
        elif page == 'notice':
            current_teacher = request.user.teacher
            if request.method == 'POST':
                the_student_id = request.POST.get('the_student')
                the_notice = request.POST.get('notice')
                notice_duration = request.POST.get('notice_last_for')

                try:
                    student = Student.objects.get(id=the_student_id)
                    notice = NoticeForStudent(
                        notice=the_notice,
                        student=student,
                        teacher=current_teacher,
                        notice_last_for=notice_duration
                    )
                    notice.save()

                    messages.success(request, 'Notice sent successfully.')

                except Student.DoesNotExist:
                    messages.error(request, 'Selected student does not exist.')
                except Exception as e:
                    messages.error(request, str(e))

            
            make_batch_objects = MakeBatch.objects.filter(teacher=current_teacher).distinct()
            notiss = NoticeForStudent.objects.filter(teacher=current_teacher)
            

            '''
            Here I did the reverse relation to do the short cut to find out all 
            students of the current teacher is teacher. for that i did reverse 
            relation with batch --> MakeBatch--> Teaacher's instance 
            and the teacher instance is logged in user. it saves minimum of 5 to 8 lines
            of codes that i used in 'your_students' page.
            '''
            all_students = Student.objects.filter(batch__makebatch__teacher=current_teacher).distinct()
            
            context = {
                'mystudent': all_students,
                'notices': notiss,
            }   
            return render(request, 'teacher/notice_for_std.html', context)


        else:
            
            # ----------- Getting the new registered student of coaching ---------
            # ------------------ who took subject with this teacher ---------------
            batch_of_teacher = MakeBatch.objects.filter(teacher=request.user.teacher)
            your_students = set()

            for b in batch_of_teacher:
                subj = get_object_or_404(Subjects, name=b.subject)
                cls = get_object_or_404(ClassWithSubject, s_class=b.class_name)
                the_student = Student.objects.filter(
                    batch_id=b.batch.id,
                    your_subjects__contains=subj.name,
                    class_subjects=cls
                ).order_by('created_at')

                for s in the_student:
                    your_students.add(s)

            items_per_page = 6  
            paginator = Paginator(list(your_students), items_per_page)
            page_number = request.GET.get('page')
            current_page = paginator.get_page(page_number)

            # --------------------------------------------------------

            # ------------------- Reminders message --------------------
            current_time = datetime.now().time()
            # one_hour_ahead = (datetime.combine(datetime.today(), current_time) + timedelta(hours=1)).time()

            reminder = []
            for b in batch_of_teacher:
                og_T = b.start_class
                
                datetime_obj = datetime.combine(datetime.today(), og_T)
                one_hour_back = datetime_obj - timedelta(hours=1)
                one_hour_back_time = one_hour_back.time()
                if current_time >= one_hour_back_time and current_time <= og_T:
                    reminder.append(b)
            # -----------------------------------------
            # print(reminder)
            context = {
                'newuser': current_page,
                'reminders' : reminder,
                
            }
            return render(request, 'teacher/dashboard.html', context)

    else:
        return render(request, 'main/404.html')



# -------------------DONE ( Settings for Teacher )----------------------

@login_required
def change_password(request):
    if request.user.role == 'student':

        if request.method == 'POST':

            form = PassChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, 'WELL DONE! আপনার পাসওয়ার্ড সফল ভাবে পরিবর্তন হয়েছে')
                login(request, user)
                return redirect('change_password')
            else:
                messages.error(request, 'Please correct the errors.')

        else:
            form = PassChangeForm(request.user)
        
        return render(request, 'student/change_password.html', {'form': form})


    elif request.user.role == 'teacher':    
        if request.method == 'POST':
            form = PassChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, 'আপনার পাসওয়ার্ড সফল ভাবে পরিবর্তন হয়েছে')
                login(request, user)
                return redirect('tchr_dashboard_home')
            else:
                messages.error(request, 'Please correct the errors below.')

        else:
            form = PassChangeForm(request.user)
        
        return render(request, 'teacher/change_password.html', {'form': form})
    
    
    # elif request.user.role == 'guardian':    

@login_required
def edit_profile(request):
    if request.user.role == 'student':
        student = request.user.student

        if request.method == 'POST':
            form = StudentEditForm(request.POST, request.FILES, instance=student)
            if form.is_valid():
                form.save()
                messages.success(request, 'আপনার প্রফাইল সফলভাবে আপডেট হয়েছে ')
                
                return redirect('edit_profile')
            else:
                messages.error(request, 'Please correct the errors below.')

        else:
            form = StudentEditForm(instance=student)
        
        return render(request, 'student/dash_settings.html', {'form': form, 'student': student})

    if request.user.role == 'teacher':
        teacher = request.user.teacher

        if request.method == 'POST':
            form = TeacherProfileForm(request.POST, request.FILES, instance=teacher)
            if form.is_valid():
                form.save()
                messages.success(request, 'Congrats! আপনার প্রফাইল সফলভাবে আপডেট হয়েছে')
                
                return redirect('edit_profile')
            else:
                messages.error(request, 'Please correct the errors below.')

        else:
            form = TeacherProfileForm(instance=teacher)
        
        return render(request, 'teacher/edit_profile.html', {'form': form, 'teacher': teacher})

@login_required
def seen_message(request, msg_id):

    if request.user.role == "student":
        if msg_id is not None:
            content = get_object_or_404(MessageForStudent, id=msg_id)
            content.visited = True
            content.save()
            context = {'sms':content}
            return render(request, 'main/m1.html', context)
        else:
            return render(request, 'main/404.html')

    elif request.user.role == "teacher":
        if msg_id is not None:
            try:
                content = get_object_or_404(MessageForTeacher, id=msg_id)
                content.visited = True
                content.save()
                context = {'sms':content}
            except:
                return render(request, 'teacher/error.html', {'error_message': ' ত্রুটি ! আপনি যে তথ্য এর রিকুয়েস্ট দিয়েছেন তা হয়ত সিস্টেমে নেই । '})
        else:
            content = "NOTHING. Its a spam"
            context = {'sms':content}


    else:
        return render(request, 'main/404.html')


    return render(request, 'main/read_msg.html', context)

@login_required
def delete_notice(request, n_id):
    note = get_object_or_404(NoticeForStudent, pk=n_id, teacher = request.user.teacher)

    if request.user.teacher == note.teacher:
        note.delete()
        messages.success(request, "এই নোটিশটি মুছে ফেলা হয়েছে।")
    else:
        messages.error(request, "আপনি ইহা মুছতে অনুমতি পাচ্ছেন না।")

    return redirect('teacher_dashb', page='notice')

@login_required
def delete_note(request, note_id):
    note = get_object_or_404(NoteAndSheet, pk=note_id, teacher = request.user.teacher)

    # Check if the logged-in teacher owns the note
    if request.user.teacher == note.teacher:
        note.delete()
        messages.success(request, "এই নোট সফলভাবে মুছে ফেলা হয়েছে।")
    else:
        messages.error(request, "আপনি এই নোট মুছতে অনুমতি পাচ্ছেন না।")

    return redirect('teacher_dashb', page='note')

@login_required
def delete_hw(request, hw_id):
    note = get_object_or_404(HomeWork, pk=hw_id, teacher = request.user.teacher)

    # Check if the logged-in teacher owns the note
    if request.user.teacher == note.teacher:
        note.delete()
        messages.success(request, "এই বাড়ির কাজটি মুছে ফেলা হয়েছে।")
    else:
        messages.error(request, "আপনি অনুমতি পাচ্ছেন না।")

    return redirect('teacher_dashb', page='hw')

@login_required
def question_and_answer_make_by_teacher(request, q_id):
    teacher = request.user.teacher
    the_category = get_object_or_404(QuizCategory, uid = q_id, teacher = teacher)

    try:
        question = get_object_or_404(Question, category_id=q_id, category__teacher=teacher)
        num_answers = question.how_many_answer_for_this_ques
    except :
        num_answers = 4

    if request.method == 'POST':
        try:
            question_text = request.POST.get('question')
            mark_ques = request.POST.get('mark_ques')
            no_option = request.POST.get('no_option')

            question = Question.objects.create(category = the_category,
                                                ques_name=question_text,
                                                mark=mark_ques,
                                                how_many_answer_for_this_ques = mark_ques,
                                                )

            for i in range(int(no_option)):
                answer_text = request.POST.get(f'answer_{i}')
                is_correct = request.POST.get('correct_answer') == str(i)
                # print(answer_text, is_correct )
                
                answer = Answer.objects.create(answer=answer_text,
                                                qustion=question,
                                                is_correct=is_correct)
            messages.success(request, "একটি নতুন কুইজ ক্যাটাগরি তৈরি হয়েছে")

        except Exception as e:
            return render(request, 'teacher/error.html', {'error_message': e})

        return redirect('teacher_dashb', page='quiz')

    else:
        question_form = QuestionForm()
        
    all_existing_questions = Question.objects.filter(category=the_category)

    context = {
        'question_form': question_form,
        'loop': num_answers,
        'my_question':all_existing_questions,
    }
    return render(request, 'teacher/question.html', context)

@login_required
def delete_question(request, q_id):
    try:
        question = Question.objects.get(uid=q_id, category__teacher = request.user.teacher)
        category = question.category
        if category.teacher == request.user.teacher:
            question.delete()
            messages.success(request, "এই প্রশ্নটি ডিলিট করা হয়েছে")
        else:
            messages.error(request, "এই প্রশ্নটি ডিলিট করার অনুমতি পাচ্ছেন না")
    except Question.DoesNotExist:
        messages.error(request, "প্রশ্ন খুজে পাওয়া যায় নি")
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))






# ============ This is for click and download file ==========

def downloadfile(request,the_model, id):
    if the_model == 'NoteAndSheet':
        model = NoteAndSheet
        files = get_object_or_404(model, id = id)
        locations = str(files.upload_note.url)
    elif the_model == 'ExamSchedule':
        model = ExamSchedule
        files = get_object_or_404(model, id = id)
        locations = str(files.file.url)
    else:
        locations = None

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    loc = locations
    filepath = base_dir + loc

    thefile = filepath
    filename = os.path.basename(thefile)
    chunk_size = 8192
    response = StreamingHttpResponse(
        FileWrapper(open(thefile, 'rb'), chunk_size),
        content_type=mimetypes.guess_type(thefile)[0],
    )
    response['Content-Length'] = os.path.getsize(thefile)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response



# =-------------------------------------------------------------------------------=
# ===================================================================================

# NOT DEVELOPED YET .
def guardian_dashb(request, page):
    if page == 'home':
        HttpResponse("OK GUARDIAN")
    else:
        return render(request, 'dash.html')
    


def temp(request):
    form = StudentForm(request.POST or None)
    context = {'form':form}
    return render(request, 'home/temp.html', context)