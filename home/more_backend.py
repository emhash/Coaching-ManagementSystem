from users.models import Student, Teacher
import random

def calculate_grade(marks, out_of):
    percentage = (marks / out_of) * 100

    if percentage >= 80:
        return 'A+'
    elif percentage >= 70:
        return 'A'
    elif percentage >= 60:
        return 'A-'
    elif percentage >= 55:
        return 'B'
    elif percentage >= 50:
        return 'C+'
    elif percentage >= 40:
        return 'C'
    elif percentage >= 30:
        return 'D'
    else:
        return 'F'

def generate_unique_integer_id():
    while True:
        random_id = random.randint(100000, 999999)  
        if not Student.objects.filter(s_id=random_id).exists():
            return random_id


def teacher_dashboard_common_data(request):
    data = 'FUTURE'
    
    context = {
        'data' : data,
    }
    return context 

