from users.models import Student
import random
# import re ,os,sys
# from docx import Document
# from docxtpl import DocxTemplate


# def demoCheck(the_file_doc,modified_file_path):
#     os.chdir(sys.path[0])
#     doc = DocxTemplate(the_file_doc)
#     context = { 'user_name  ' : "World company" }
#     doc.render(context)
#     doc.save(modified_file_path)

# def myreplace(file, regex, replace):
#     for p in file.paragraphs:
#         if regex.search(p.text):
#             inline=p.runs
#             for i in range(len(inline)):
#                 if regex.search(inline[i].text):
#                     text=regex.sub(replace, inline[i].text)
#                     inline[i].text=text
#     for table in file.tables:
#         for row in table.rows:
#             for cell in row.cells:
#                 myreplace(cell, regex, replace)


# def ReadingTextDocuments(fileName): 

#     doc = Document (fileName)
#     completedText = []
#     for paragraph in doc.paragraphs: 
#         completedText.append (paragraph.text)
#     return '\n'.join(completedText)


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

