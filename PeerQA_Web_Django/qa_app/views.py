from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.templatetags.static import static
from .forms import QuestionForm
from .models import Question, Comment
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.contrib.auth.models import User

lectures = {"Lecture 8: Storage (2)": 21, "Lecture 9: Indexing (1)": 40
            , "Lecture 10: Indexing (2)": 36}
lecture_dir = {"Lecture 8: Storage (2)": "L08", "Lecture 9: Indexing (1)": "L09"
            , "Lecture 10: Indexing (2)": "L10"}

# Create your views here.
def signout(request):
    if request.method == 'GET':

        if request.user.is_authenticated:
            logout(request)
            return redirect("/question/signin/")
        else:
            return HttpResponse(status=401)

    else:
        return HttpResponseNotAllowed(['GET'])

def question_list(request):
    if request.user.is_authenticated:
        context = {"question_list": Question.objects.all()}
        return render(request, "view/question_list.html", context)
    else:
        return redirect("/question/signin/")


def question_form(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            form = QuestionForm()
            return render(request, "view/question_form.html", {"form": form, "lectures": lectures})
        elif request.method == "POST":
            form = QuestionForm(request.POST)
            if form.is_valid():
                form.save()
            return redirect("/question/")
    else:
        return redirect("/question/signin/")

def question_detail(request, id):
    if request.user.is_authenticated:
        question = Question.objects.get(pk=id)

        file_name = "/Page" + str(question.lecture_slide) + ".jpeg"
        src_text = static("lecture/" + lecture_dir[question.lecture_name] + file_name)

        context = {"question": question, "src_text": src_text}
        return render(request, "view/question_detail.html", context)
    else:
        return redirect("/question/signin/")

def question_delete(request, id):
    if request.user.is_authenticated:
        question = Question.objects.get(pk=id)
        question.delete()

        return redirect("/question/")
    else:
        return redirect("/question/signin/")

def load_pages(request):
    if request.user.is_authenticated:
        lecture_id = request.GET.get('lecture_id')
        pages = []
        if (lecture_id != ""):
            pages = range(1, lectures[lecture_id]+1)
        return render(request, 'component/page_dropdown_options.html', {'pages': pages})
    else:
        return redirect("/question/signin/")

def load_slide(request):
    lecture = request.GET.get('lecture')
    slide = request.GET.get('slide')

    file_name = "/Page" + slide + ".jpeg"
    src = static("lecture/" + lecture_dir[lecture] + file_name)
    
    return HttpResponse(src)


def signin_page(request):
    if request.method == "GET":
        return render(request, "view/signin.html")
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user=user)
            return redirect("/question/")
        return HttpResponse(status=401)


def signup_page(request):
    if request.method == "GET":
        return render(request, "view/signup.html")
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        User.objects.create_user(username=username, password=password, first_name=first_name)
        return redirect("/question/signin/")

@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])
