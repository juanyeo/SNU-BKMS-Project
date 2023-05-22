from django.db import models
from django.contrib.auth.models import AbstractUser
# User에서 비밀번호 설정 할 때 너무 쉬운 비밀번호는 장고에서 자동으로 암호를 띄우는 것 같음. ex) b는 안 되도, bi는 됨
# 학번 = username, 비밀번호 = password, 닉네임 = first_name (기본 장고 유저를 사용하다 보니 이렇게 되었음) is staff 도 기본적으로 제공.
# pip install psycopg2-binary
# Create your models here.

class User(AbstractUser):
    owner_accepted = models.IntegerField(default=0)
    admin_accepted = models.IntegerField(default=0)
    question_num = models.IntegerField(default=0)
    comment_num = models.IntegerField(default=0)
    scrap_num = models.IntegerField(default=0)


class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=2000)
    status = models.CharField(max_length=12)
    lecture_name = models.CharField(max_length=50)
    lecture_slide = models.IntegerField()
    postDate = models.DateTimeField(auto_now=True)
    tag = models.CharField(max_length=24)
    subject = models.IntegerField(default=1)


class Comment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=2000)
    owner_accepted = models.IntegerField()
    admin_accepted = models.IntegerField()
    postDate = models.DateTimeField(auto_now=True)


class Scrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
