from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.templatetags.static import static
from .forms import QuestionForm
from .models import Question, Comment

lectures = {"Lecture 8: Storage (2)": 21, "Lecture 9: Indexing (1)": 40
            , "Lecture 10: Indexing (2)": 36}
lecture_dir = {"Lecture 8: Storage (2)": "L08", "Lecture 9: Indexing (1)": "L09"
            , "Lecture 10: Indexing (2)": "L10"}

# Create your views here.
def question_list(request):
    context = {"question_list": Question.objects.all()}
    return render(request, "view/question_list.html", context)


def question_form(request):
    if request.method == "GET":
        form = QuestionForm()
        return render(request, "view/question_form.html", {"form": form, "lectures": lectures})
    elif request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect("/question/")

def question_detail(request, id):
    question = Question.objects.get(pk=id)
    
    file_name = "/Page" + str(question.lecture_slide) + ".jpeg"
    src_text = static("lecture/" + lecture_dir[question.lecture_name] + file_name)

    context = {"question": question, "src_text": src_text}
    return render(request, "view/question_detail.html", context)

def question_delete(request, id):
    question = Question.objects.get(pk=id)
    question.delete()

    return redirect("/question/")

def load_pages(request):
    lecture_id = request.GET.get('lecture_id')
    pages = []
    if (lecture_id != ""):
        pages = range(1, lectures[lecture_id]+1)
    return render(request, 'component/page_dropdown_options.html', {'pages': pages})

def load_slide(request):
    lecture = request.GET.get('lecture')
    slide = request.GET.get('slide')

    file_name = "/Page" + slide + ".jpeg"
    src = static("lecture/" + lecture_dir[lecture] + file_name)
    
    return HttpResponse(src)
