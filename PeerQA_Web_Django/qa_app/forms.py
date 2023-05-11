from django import forms
from .models import Question, Comment, User


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ("title", "content", "status", "lecture_name", "lecture_slide", "user")  # '__all__'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content", "question", "user")  # '__all__'
