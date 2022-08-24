import logging

from django.http import HttpResponseNotFound
from django.views import generic

from .models import Lesson, Course, CoursesForUsers


# logger = logging.getLogger(__name__)


class CourseView(generic.DetailView):
    model = Course
    context_object_name = 'course'
    queryset = Course.objects.select_related('picture').prefetch_related('lessons')

    def get_context_data(self, **kwargs):
        # проверяем, показывать ли пользователю ссылки на уроки
        context = super().get_context_data(**kwargs)
        # print("context", context)
        if context.get("course").is_free or \
                (self.request.user.is_authenticated and
                 self.request.user.has_perm('app_lessons.view_lesson')):
            context['can_see'] = True
        else:
            context['can_see'] = False
        if self.request.user.is_authenticated:
            # TODO ...возможно, понадобится показать кнопку "подключите мне этот курс",
            #  если записи с таким курсом для этого юзера нет, либо ничего не показывать,
            #  если запись с is_active=False
            rel = CoursesForUsers.objects.filter(user=self.request.user,
                                                 course=context.get("course"), is_active=True).first()
            if rel:
                context['course_paid'] = True
        return context

    def dispatch(self, request, pk, *args, **kwargs):
        # смотреть неготовые курсы можно только редактору,
        # остальным - неготовых курсов как бы нет совсем
        res = super().dispatch(request, pk, *args, **kwargs)
        if res.context_data['course'].status != Course.OK:
            if not request.user.is_authenticated or not request.user.has_perm('app_lessons.view_course'):
                return HttpResponseNotFound()
        return res


class LessonView(generic.DetailView):
    model = Lesson
    context_object_name = 'lesson'
    queryset = Lesson.objects.select_related('course').select_related('picture')

    def get_context_data(self, **kwargs):
        # проверяем, показывать ли пользователю информацию из урока
        context = super().get_context_data(**kwargs)
        lesson = context.get("lesson")
        if lesson.course.is_free or lesson.is_intro or \
                (self.request.user.is_authenticated and
                 self.request.user.has_perm('app_lessons.view_lesson')):
            context['can_see'] = True
        else:
            context['can_see'] = False
        if self.request.user.is_authenticated:
            rel = CoursesForUsers.objects.filter(user=self.request.user,
                                                 course=context.get("lesson").course,
                                                 is_active=True).first()
            if rel:
                context['course_paid'] = True
        return context

    def dispatch(self, request, pk, *args, **kwargs):
        # смотреть уроки для неготовых курсов можно только редактору,
        # остальным - таких уроков как бы нет совсем
        res = super().dispatch(request, pk, *args, **kwargs)
        if res.context_data['lesson'].course.status != Course.OK:
            if not request.user.is_authenticated or not request.user.has_perm('app_lessons.view_lesson'):
                return HttpResponseNotFound()
        return res


class CourseListView(generic.ListView):
    model = Course
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.filter(status=Course.OK).select_related('category').\
            order_by('category__id').all()
