from django.urls import path, include
from qa_app import views
from django.views.generic import RedirectView

urlpatterns = [
    path("", views.question_list),  # address:8080/question/
    path("2/", views.question_list2),
    path("form/", views.question_form),  # address:8080/question/form
    path("delete/<int:id>", views.question_delete, name="question_delete"),
    path("detail/<int:id>", views.question_detail, name="question_detail"),
    path("comment_admin_like/<int:id>", views.comment_admin_like, name="comment_admin_like"),
    path("comment_owner_like/<int:id>", views.comment_owner_like, name="comment_owner_like"),
    path("signin/", views.signin_page, name="signin_page"),
    path("signup/", views.signup_page, name="signup_page"),
    path("signout/", views.signout, name='signout'),
    path('ajax/load_pages/', views.load_pages, name='ajax_load_pages'),
    path('ajax/load_slide/', views.load_slide, name='ajax_load_slide'),
    path("mypage/", views.mypage, name="mypage"),
    path("signout/", views.signout, name="signout"),
    path("scrap/", views.scrap, name="scrap"),
    path("olap/", views.olap, name="olap_page"),
]