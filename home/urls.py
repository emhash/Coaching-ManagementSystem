from django.views.generic import RedirectView
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
urlpatterns = [
    path('', home, name="home"),
    path('registration/', registration, name="registration"),
    path('logout/', logout_view, name="logout"),  
    path('userlogin/', userlogin, name="userlogin"),  
    path('profile/change_password/', change_password, name='change_password'),
    path('profile/settings/', edit_profile, name='edit_profile'),

    # Student
    path('student_dashboard/home', student_dashb, name="std_dashboard_home"), 
    path('student_dashboard/', RedirectView.as_view(pattern_name='std_dashboard_home')),
    path('student_dashboard/<str:page>', student_dashb, name="student_dashb"),
    
    
    #   TEACHER ALL DASHBOARD LINK --->
    path('teacher_dashboard/home', teacher_dashb, name="tchr_dashboard_home"), 
    path('teacher_dashboard/', RedirectView.as_view(pattern_name='tchr_dashboard_home')),
    path('teacher_dashboard/<str:page>', teacher_dashb, name="teacher_dashb"),  
    path('teacher_dashboard/add_mark/<str:shift>/', add_mark1, name='add_mark1'),
    path('teacher_dashboard/add_mark/<str:shift>/<str:cls>/', add_mark2, name='add_mark2'),
    path('teacher_dashboard/add_mark/<str:shift>/<str:cls>/<str:subject>/', add_mark3, name='add_mark3'),
    path('teacher_dashboard/add_mark/<str:shift>/<str:cls>/<str:subject>/<str:exam>/', add_mark4, name='add_mark4'),


    #   GUARDIAN ALL DASHBOARD LINK --->
    path('guardian_dashboard/home', guardian_dashb, name="grdiun_dashboard_home"), 
    path('guardian_dashboard/', RedirectView.as_view(pattern_name='grdiun_dashboard_home')),
    path('guardian_dashboard/<str:page>', guardian_dashb, name="guardian_dashb"),  
    
    path('register/', register_role, name='register_role'),
    path('authentication/', authentication, name='authentication'),

    path('temp/', temp, name='temp'),




]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)