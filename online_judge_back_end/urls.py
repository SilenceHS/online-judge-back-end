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
    path('api/getquizlist/<str:courseid>/<str:username>',views.quizList),
    path('api/getquiz/<str:courseid>/<str:quizurl>/<str:username>', views.getQuiz),
    path('api/postquiz/',views.postQuiz),
    path('api/gettempstatus/',views.getTempStatus),
    path('api/addquiz/',views.addQuiz),
    path('api/deleteQuiz/',views.deleteQuiz),
    path('api/getmodifyquiz/<str:courseId>/<str:quizUrl>/<str:userName>',views.getModifyQuiz),
    path('api/gmodifyquiz/',views.modifyQuiz),
]
