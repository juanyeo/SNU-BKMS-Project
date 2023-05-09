from django.db import models
from django.contrib.auth.models import User

# pip install psycopg2-binary
# Create your models here.
class Question(models.Model):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=400)
    status = models.CharField(max_length=12)
    lecture_name = models.CharField(max_length=24)
    lecture_slide = models.IntegerField()
    postBy = models.CharField(max_length=12)
    postDate = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.CharField(max_length=400)
    owner_accepted = models.IntegerField()
    admin_accepted = models.IntegerField()
    postBy = models.IntegerField()
    postDate = models.DateTimeField(auto_now=True)






