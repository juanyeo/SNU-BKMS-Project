from django.urls import path, include
from qa_app import views
from django.views.generic import RedirectView

urlpatterns = [
    path("", views.question_list),  # address:8080/question/
    path("form/", views.question_form),  # address:8080/question/form
    path("delete/<int:id>", views.question_delete, name="question_delete"),
    path("detail/<int:id>", views.question_detail, name="question_detail"),
    path("signin/", views.signin_page, name="signin_page"),
    path("signin/", views.signin_button, name="signin_button"),
    path("signup/", views.signup_page, name="signup_page"),
    path('ajax/load_pages/', views.load_pages, name='ajax_load_pages'),
    path('ajax/load_slide/', views.load_slide, name='ajax_load_slide'),
]