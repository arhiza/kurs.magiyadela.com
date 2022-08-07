from django.shortcuts import render, get_object_or_404
from django.views import generic

from .models import Lesson, Course


class CourseView(generic.DetailView):
    model = Course

    def dispatch(self, request, pk, *args, **kwargs):
        # смотреть неготовые курсы можно только редактору,
        # остальным - неготовых курсов как бы нет совсем
        if request.user.is_authenticated and self.request.user.has_perm('app_lessons.view_course'):
            course = get_object_or_404(Course, pk=pk)
        else:
            course = get_object_or_404(Course, status=Course.OK, pk=pk)
        return super().dispatch(request, pk, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # проверяем, показывать ли пользователю ссылки на уроки
        context = super().get_context_data(**kwargs)
        if context.get("course").is_free or \
                (self.request.user.is_authenticated and
                 self.request.user.has_perm('app_lessons.view_lesson')):
            context['can_see'] = True
        else:
            context['can_see'] = False
        # if self.request.user.is_authenticated:  # TODO ...AND у юзера куплен этот курс
        #     context['course_paid'] = True
        # else:
        #    context['course_paid'] = False
        return context


class LessonView(generic.DetailView):
    model = Lesson

    def dispatch(self, request, pk, *args, **kwargs):
        # смотреть уроки для неготовых курсов можно только редактору,
        # остальным - таких уроков как бы нет совсем
        if request.user.is_authenticated and self.request.user.has_perm('app_lessons.view_lesson'):
            lesson = get_object_or_404(Lesson, pk=pk)
        else:
            lesson = get_object_or_404(Lesson, course__status=Course.OK, pk=pk)
        return super().dispatch(request, pk, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # проверяем, показывать ли пользователю информацию из урока
        context = super().get_context_data(**kwargs)
        if context.get("lesson").course.is_free or \
                (self.request.user.is_authenticated and
                 self.request.user.has_perm('app_lessons.view_lesson')):
            context['can_see'] = True
        else:
            context['can_see'] = False
        # if self.request.user.is_authenticated:  # TODO ...AND у юзера куплен этот курс
        #    context['course_paid'] = True
        # else:
        #    context['course_paid'] = False
        return context


class CourseListView(generic.ListView):
    model = Course
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.filter(status=Course.OK).all()
