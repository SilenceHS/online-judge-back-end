"""online_judge_back_end URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from online_judge_back_end import views
urlpatterns = [
    path('api/login/', views.login),
    path('api/register/', views.firstRegister),
    path('api/active/<str:key>', views.active),
    path('admin/', admin.site.urls),
    path('api/getquizlist/<str:courseurl>/<str:username>',views.quizList),
    path('api/getquiz/<str:courseurl>/<str:quizurl>/<str:username>', views.getQuiz),
    path('api/postquiz/',views.postQuiz),
    path('api/gettempstatus/',views.getTempStatus),
    path('api/addquiz/',views.addQuiz),
    path('api/deleteQuiz/',views.deleteQuiz),
    path('api/getmodifyquiz/<str:courseId>/<str:quizUrl>/<str:userName>',views.getModifyQuiz),
    path('api/modifyquiz/',views.modifyQuiz),
    path('api/getcourselist/<str:userName>/<str:type>',views.getCourseList),
    path('api/modifycourse/',views.modifyCourse),
    path('api/addcourse/',views.addCourse),
    path('api/deletecourse/',views.deleteCourse),
    path('api/selectcourse/',views.selectCourse),
    path('api/deleteselectedcourse/',views.deleteSelectedCourse),
    path('api/modifystudentcoursename/',views.modifyStudentCourseName),
    path('api/showrank/<str:url>/<str:userName>', views.showRank),
    path('api/getExcel/<str:url>', views.getExcel),
    path('api/getMainCount/', views.getMainCount),
    path('api/resetPass/', views.resetPass),
    path('api/gethistorylist/<str:url>/<str:userName>', views.getHistoryList),



]
