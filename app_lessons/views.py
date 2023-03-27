# import logging

from django.db.models import Prefetch
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import JoinToCourse, AddCommentForm
from .models import Lesson, Course, CoursesForUsers, Category, Comment
from app_emails.services import mail_about_new_order, mail_about_new_comment
from app_users.models import SiteSettings


# logger = logging.getLogger(__name__)


class CourseView(generic.DetailView):
    model = Course
    slug_field = 'url'
    context_object_name = 'course'
    queryset = Course.objects.select_related('picture').prefetch_related('lessons').\
        prefetch_related('to_users')

    def get_context_data(self, **kwargs):
        # проверяем, показывать ли пользователю ссылки на уроки
        context = super().get_context_data(**kwargs)
        can_see = False
        if self.request.user.is_authenticated:
            rel = context.get('course').to_users.filter(user=self.request.user).first()
            context['course_paid'] = rel
            if not rel:
                form = JoinToCourse(initial={'course_id': context.get('course').id})
                context['form'] = form
            else:
                if rel.is_active:
                    can_see = True
                else:
                    context['info_about_order'] = "Заявка на включение курса отправлена администратору. " \
                                                  "Скоро всё будет подключено. Но это не точно."
        else:
            loginurl = reverse("login")
            nexturl = context.get('course').get_absolute_url()
            context['info_about_order'] = f"Запись на курс доступна <a href={loginurl}?next=" \
                                          f"{nexturl}>авторизованным</a> пользователям."
        if not can_see and (context.get('course').is_free or
                            (self.request.user.is_authenticated and
                             self.request.user.has_perm('app_lessons.view_lesson'))):
            can_see = True
        context['can_see'] = can_see
        return context

    def dispatch(self, request, *args, **kwargs):
        # смотреть неготовые курсы можно только редактору,
        # остальным - неготовых курсов как бы нет совсем
        res = super().dispatch(request, *args, **kwargs)
        if request.method == "POST":
            return res
        if res.context_data['course'].status != Course.OK:
            if not request.user.is_authenticated or not request.user.has_perm('app_lessons.view_course'):
                return HttpResponseNotFound()
        return res

    def post(self, request, *args, **kwargs):
        form = JoinToCourse(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            pk = form.cleaned_data['course_id']
            user = request.user
            rel = CoursesForUsers.objects.filter(course__id=pk, user=user).first()
            if not rel:
                course = Course.objects.get(pk=pk)
                if course.is_free:
                    CoursesForUsers.objects.create(course=course, user=user, is_active=True,
                                                   info='(самостоятельно на бесплатный курс)')
                else:
                    cfu = CoursesForUsers.objects.create(course=course, user=user, is_active=False)
                    mail_about_new_order(cfu)
        return HttpResponseRedirect(reverse('course', kwargs=kwargs))


class LessonView(generic.DetailView):
    model = Lesson
    slug_field = 'url'
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

    def dispatch(self, request, *args, **kwargs):
        # смотреть уроки для неготовых курсов можно только редактору,
        # остальным - таких уроков как бы нет совсем
        res = super().dispatch(request, *args, **kwargs)
        if res.context_data['lesson'].course.status != Course.OK:
            if not request.user.is_authenticated or not request.user.has_perm('app_lessons.view_lesson'):
                return HttpResponseNotFound()
        return res


class AddCommentView(generic.View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AddCommentView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        lesson = Lesson.objects.get(url=kwargs.get("slug"))
        context = {"lesson": lesson, "form": AddCommentForm()}
        return render(request, "app_lessons/add_comment.html", context=context)

    def post(self, request, *args, **kwargs):
        lesson = Lesson.objects.get(url=kwargs.get("slug"))
        form = AddCommentForm(request.POST)
        if form.is_valid():
            text_question = form.data.get("text")
            user = request.user
            comm = Comment.objects.create(lesson=lesson, user=user, text_question=text_question)
            mail_about_new_comment(request, comm)
            messages.success(request, "Комментарий отправлен")
            return HttpResponseRedirect(reverse('lesson', kwargs=kwargs))
        context = {"lesson": lesson, "form": form}
        return render(request, "app_lessons/add_comment.html", context=context)


class CourseListView(generic.ListView):
    model = Course
    context_object_name = 'categories'

    def get_queryset(self):
        ok_courses = Course.objects.filter(status=Course.OK)
        return Category.objects.prefetch_related(Prefetch('courses', queryset=ok_courses))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        main_page_text = SiteSettings.objects.filter(key="main_page").first()
        if main_page_text:
            context['main_page_text'] = main_page_text.text_value
        return context


def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)
