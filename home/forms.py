from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django import forms
from users.models import CustomUser, Student, Teacher, HomeWork, MakeBatch, Question,Answer, ApplyForLeave, NoticeForStudent
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm

class CommonRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields =['email','phone_number', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form__input', 'placeholder': 'আপনার ইমেইল লিখুন'})
        self.fields['email'].label = 'Email'
        self.fields['phone_number'].widget.attrs.update({'class': 'form__input', 'placeholder': 'আপনার ফোন নম্বার দিন '})
        self.fields['phone_number'].label = 'phone_number'

        self.fields['password1'].widget.attrs.update({'class': 'form__input', 'placeholder': 'পাসওয়ার্ড সেট করুন '})
        self.fields['password1'].label = 'Password'

        self.fields['password2'].widget.attrs.update({'class': 'form__input', 'placeholder': 'পুনরায় পাসওয়ার্ড নিশ্চিত করুন '})
        self.fields['password2'].label = 'Confirm Password'




class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = (
            's_name', 'class_subjects', 'guardian_phone', 's_phone', 'guardian_email','shift',
        )   

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

        placeholders = {
            's_name': 'শিক্ষার্থী সম্পূর্ণ নাম ',
            'class_subjects': 'যে ক্লাসে ভর্তি হবেন তা নির্বাচন করুন *',
            'guardian_phone': 'অভিবাবক এর মোবাইল নাম্বার (আবশ্যিক) *',
            's_phone': 'আপনার মোবাইল নাম্বার (Optional)',
            'guardian_email': 'অভিবাবক এর ইমেইল (Optional))',
            'shift': 'যে Shift ভর্তি হবেন তা নির্বাচন করুন *',
        }

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form__input'
            self.fields[field_name].widget.attrs['placeholder'] = placeholders[field_name]

    def clean_guardian_phone(self):
        guardian_phone = self.cleaned_data.get('guardian_phone')
        # Add your validation logic here
        if not guardian_phone.isdigit():
            raise ValidationError('Guardian phone number should only contain digits.')
        return guardian_phone
    
    def clean_s_name(self):
        s_name = self.cleaned_data.get('s_name')
        # Add your validation logic here
        if s_name is None:
            raise ValidationError('Can not be empty')
        return s_name
    
    def clean_class_subjects(self):
        class_subjects = self.cleaned_data.get('class_subjects')
        # Add your validation logic here
        if class_subjects is None:
            raise ValidationError('why empty')
        return class_subjects
    
    def clean_s_phone(self):
        s_phone = self.cleaned_data.get('s_phone')
        # Add your validation logic here
        if not s_phone is None:
            if not s_phone.isdigit():
                raise ValidationError('Phone number should only contain digits.')     
        return s_phone
    
    def clean_guardian_email(self):
        guardian_email = self.cleaned_data.get('guardian_email')
        # Add your validation logic here
        return guardian_email


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = (
            't_name', 't_present_adress', 't_permnt_adress', 't_extra_phone',
        )

    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)

        placeholders = {
            't_name': 'সম্পূর্ণ নাম ',
            't_present_adress': 'Present adress *',
            't_permnt_adress': 'Permanent adress *',
            't_extra_phone': 'মোবাইল নাম্বার (Optional)',
            
        }
        
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form__input'
            self.fields[field_name].widget.attrs['placeholder'] = placeholders[field_name]
    
    def clean_t_name(self):
        t_name = self.cleaned_data.get('t_name')
        if not t_name:
            raise ValidationError('দুঃখিত! ইহা খালি রাখা যাবে না! ')
        return t_name
    
    def clean_t_present_adress(self):
        t_present_adress = self.cleaned_data.get('t_present_adress')
        if not t_present_adress:
            raise ValidationError('দুঃখিত! ইহা খালি রাখা যাবে না! ')
        return t_present_adress
    
    def clean_t_permnt_adress(self):
        t_permnt_adress = self.cleaned_data.get('t_permnt_adress')
        if not t_permnt_adress:
            raise ValidationError('দুঃখিত! ইহা খালি রাখা যাবে না! ')
        return t_permnt_adress
    
    def clean_t_extra_phone(self):
        t_extra_phone = self.cleaned_data.get('t_extra_phone')
        if not t_extra_phone:
            return t_extra_phone  # Allow it to be optional
        if not t_extra_phone.isdigit():
            raise ValidationError('মোবাইল নম্বর শুধু সংখ্যা হতে হবে ')
        return t_extra_phone

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['t_name', 'profile_pic', 'teacher_background', 't_present_adress', 't_permnt_adress', 't_extra_phone']
        labels = {
            't_name': 'সম্পূর্ণ নাম',
            'profile_pic': 'আপনার ছবি',
            'teacher_background': 'ব্যাকগ্রাউন্ড',
            't_present_adress': 'বর্তমান ঠিকানা',
            't_permnt_adress': 'স্থায়ী ঠিকানা',
            't_extra_phone': 'বাড়তি মোবাইল নাম্বার',
        }

    def __init__(self, *args, **kwargs):
        super(TeacherProfileForm, self).__init__(*args, **kwargs)

        placeholders = {
            't_name': 'সম্পূর্ণ নাম ',
            'profile_pic': 'আপনার ছবি',
            'teacher_background': 'ব্যাকগ্রাউন্ড ',
            't_present_adress': 'বর্তমান ঠিকানা',
            't_permnt_adress': 'স্থায়ী ঠিকানা  ',
            't_extra_phone': 'বাড়তি মোবাইল নাম্বার',
        }

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'input-field'
            
            self.fields[field_name].widget.attrs['placeholder'] = placeholders[field_name]


class PassChangeForm(BasePasswordChangeForm):
    class Meta:
        model = CustomUser 
        fields = ['old_password', 'new_password1', 'new_password2']
    def __init__(self, *args, **kwargs):
        super(PassChangeForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'input-field'



class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            's_name',
            's_phone',
            'guardian_email',
            'profile_pic',
            
        ]

        labels = {
            's_name': 'সম্পূর্ণ নাম',
            'profile_pic': 'তোমার ছবি',
            's_id': 'তোমার আইডি ',
            's_phone': 'তোমার মোবাইল নাম্বার',
        }

    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'input-field'

  

class HomeWorkForm(forms.ModelForm):
    last_day_of_submit = forms.DateField(
    widget=forms.TextInput(attrs={'type': 'date'}),
    input_formats=['%Y-%m-%d']
        )
    class Meta:
        model = HomeWork
        fields = ['title', 'hw_detail', 'last_day_of_submit', 'for_class', 'batch', 'subject']

    def __init__(self, *args, **kwargs):
        super(HomeWorkForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'input-field'

        self.fields['last_day_of_submit'].widget.attrs['placeholder'] = "Ex: 2023-11-12"
        

  
from users.models import NoteAndSheet

class NoteAndSheetForm(forms.ModelForm):
    class Meta:
        model = NoteAndSheet
        fields = ['title', 'for_class', 'batch', 'subject', 'upload_note']

    def __init__(self, *args, **kwargs):
        super(NoteAndSheetForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'input-field'

  

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['ques_name', 'mark', 'how_many_answer_for_this_ques']

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'input-field'

  

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['answer', 'is_correct']

    def __init__(self, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'input-field'

  

class ApplyLeaveForm(forms.ModelForm):
    class Meta:
        model = ApplyForLeave
        fields = ['reason_for_apply', 'description', 'attachment']

    def __init__(self, *args, **kwargs):
        super(ApplyLeaveForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'input-field'

