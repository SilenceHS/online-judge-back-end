# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Answerlist(models.Model):
    userid = models.ForeignKey('User', models.CASCADE, db_column='userid', blank=True, null=True)
    quizid = models.ForeignKey('Quiz', models.CASCADE, db_column='quizid', blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=30, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    usetime = models.IntegerField(blank=True, null=True)
    usememory = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'answerlist'


class Course(models.Model):
    teacherid = models.ForeignKey('User', models.CASCADE, db_column='teacherid', blank=True, null=True)
    coursename = models.CharField(max_length=255, blank=True, null=True)
    detail = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=7, blank=True, null=True)
    teachername = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course'


class Quiz(models.Model):
    url = models.CharField(max_length=32, blank=True, null=True)
    courseid = models.ForeignKey(Course, models.CASCADE, db_column='courseid', blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    input = models.TextField(blank=True, null=True)
    output = models.TextField(blank=True, null=True)
    sampleinput = models.CharField(max_length=255, blank=True, null=True)
    sampleoutput = models.CharField(max_length=255, blank=True, null=True)
    level = models.CharField(max_length=10, blank=True, null=True)
    language = models.CharField(max_length=255, blank=True, null=True)
    timelimit = models.IntegerField(blank=True, null=True)
    memorylimit = models.IntegerField(blank=True, null=True)
    tag = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'quiz'


class User(models.Model):
    username = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=36, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'


class UserCourse(models.Model):
    courseid = models.ForeignKey(Course, models.CASCADE, db_column='courseid', blank=True, null=True)
    studentid = models.ForeignKey(User, models.CASCADE, db_column='studentid', blank=True, null=True)
    studentname = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user-course'
