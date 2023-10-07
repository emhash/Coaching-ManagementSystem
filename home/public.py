from users.models import MessageForTeacher, MessageForStudent

def common_data(request):
    try:
        if request.user.role == "student":
            try:
                
                unviewed_msg_std = MessageForStudent.objects.filter(message_for = request.user.student, visited = False).count()

            except:
                
                unviewed_msg_std = 0
        
            context = {
                'unviewed_msg_std' : unviewed_msg_std,
                
            }

        elif request.user.role == "teacher":
            try:
                unviewed_msg = MessageForTeacher.objects.filter(message_for = request.user.teacher, visited = False).count()
                

            except:
                unviewed_msg = 0
                
        
            context = {
                'unviewed_msg' : unviewed_msg,
                
            }
        else:
            context={}
            
    except:
        context = {}
    return context 

