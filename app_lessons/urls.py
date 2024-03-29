from django.urls import path

from .views import CourseView, LessonView, CourseListView, AddCommentView

urlpatterns = [
    path('', CourseListView.as_view(), name='all_courses'),
    path('kurs/<slug:slug>', CourseView.as_view(), name='course'),
    path('urok/<slug:slug>', LessonView.as_view(), name='lesson'),
    path('comment/<slug:slug>', AddCommentView.as_view(), name='comment'),
]
