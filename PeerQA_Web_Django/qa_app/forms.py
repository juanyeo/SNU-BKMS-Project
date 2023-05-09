from django import forms
from .models import Question, Comment, User


class SigninForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("student_id", "password")


class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("student_id", "password", "nickname")


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ("title", "content", "status", "lecture_name", "lecture_slide", "postBy")  # '__all__'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content", "postBy")  # '__all__'


