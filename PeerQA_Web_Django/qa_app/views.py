from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.templatetags.static import static
from .forms import QuestionForm, CommentForm
from .models import Question, Comment
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from .models import User

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
            return render(request, "view/question_form.html", {"form": form, "lectures": lectures, "user": request.user})
        elif request.method == "POST":
            form = QuestionForm(request.POST)
            qn = request.user.question_num
            qn += 1
            User.objects.filter(pk=request.user.id).update(question_num=qn)
            if form.is_valid():
                form.save()
            return redirect("/question/")
    else:
        return redirect("/question/signin/")

def question_detail(request, id):
    if request.user.is_authenticated:
        if request.method == "GET":
            question = Question.objects.get(pk=id)
            comments = Comment.objects.filter(question__exact=id)

            file_name = "/Page" + str(question.lecture_slide) + ".jpeg"
            src_text = static("lecture/" + lecture_dir[question.lecture_name] + file_name)
            context = {"question": question, "src_text": src_text, "user": request.user, "comment_list": comments}
            request.session["qid"] = id

            return render(request, "view/question_detail.html", context)
        elif request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.owner_accepted = 0
                post.admin_accepted = 0
                post.save()
            qid = request.session["qid"]
            return redirect("question_detail", id=qid)
    else:
        return redirect("/question/signin/")

def question_delete(request, id):
    if request.user.is_authenticated:
        question = Question.objects.get(pk=id)
        question.delete()

        return redirect("/question/")
    else:
        return redirect("/question/signin/")

def comment_admin_like(request, id):
    if request.user.is_authenticated:
        Comment.objects.filter(pk=id).update(admin_accepted=1)
        u = Comment.objects.get(pk=id).user
        aa = u.admin_accepted
        aa += 1
        User.objects.filter(id=u.id).update(admin_accepted=aa)
        qid = request.session["qid"]
        return redirect("question_detail", id=qid)
    else:
        return redirect("/question/signin/")

def comment_owner_like(request, id):
    if request.user.is_authenticated:
        c = Comment.objects.filter(pk=id)
        c.update(owner_accepted=1)
        u = Comment.objects.get(pk=id).user
        ua = u.owner_accepted
        ua += 1
        User.objects.filter(id=u.id).update(owner_accepted=ua)

        qid = request.session["qid"]
        if request.user.is_staff:
            c.update(admin_accepted=1)
            aa = u.admin_accepted
            aa += 1
            User.objects.filter(id=u.id).update(admin_accepted=aa)
        return redirect("question_detail", id=qid)
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
        User.objects.create_user(username=username, password=password, first_name=first_name,
                                    owner_accepted=0, admin_accepted=0, question_num=0)
        return redirect("/question/signin/")

@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])
