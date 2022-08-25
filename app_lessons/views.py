import logging

from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .forms import JoinToCourse
from .models import Lesson, Course, CoursesForUsers


# logger = logging.getLogger(__name__)


class CourseView(generic.DetailView):
    model = Course
    context_object_name = 'course'
    queryset = Course.objects.select_related('picture').prefetch_related('lessons').\
        prefetch_related('to_users')

    def get_context_data(self, **kwargs):
        # проверяем, показывать ли пользователю ссылки на уроки
        context = super().get_context_data(**kwargs)
        can_see = False
        if self.request.user.is_authenticated:
            # TODO ...возможно, понадобится показать кнопку "подключите мне этот курс",
            #  если записи с таким курсом для этого юзера нет, либо ничего не показывать,
            #  если запись с is_active=False
            rel = context.get('course').to_users.filter(user=self.request.user).first()
            context['course_paid'] = rel
            if not rel:
                form = JoinToCourse()
                context['form'] = form
            if rel and rel.is_active:
                can_see = True
        if can_see or context.get("course").is_free or \
                (self.request.user.is_authenticated and
                 self.request.user.has_perm('app_lessons.view_lesson')):
            context['can_see'] = True
        else:
            context['can_see'] = False
        return context

    def dispatch(self, request, pk, *args, **kwargs):
        # смотреть неготовые курсы можно только редактору,
        # остальным - неготовых курсов как бы нет совсем
        res = super().dispatch(request, pk, *args, **kwargs)
        if request.method == "POST":
            return res
        if res.context_data['course'].status != Course.OK:
            if not request.user.is_authenticated or not request.user.has_perm('app_lessons.view_course'):
                return HttpResponseNotFound()
        return res

    def post(self, request, pk, *args, **kwargs):
        form = JoinToCourse(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            user = request.user
            rel = CoursesForUsers.objects.filter(course__id=pk, user=user).first()
            if not rel:
                course = Course.objects.get(pk=pk)
                if course.is_free:
                    CoursesForUsers.objects.create(course=course, user=user, is_active=True, info='(самостоятельно на бесплатный курс)')
                else:
                    CoursesForUsers.objects.create(course=course, user=user, is_active=False)
        return HttpResponseRedirect(reverse('course', args=[pk]))


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
