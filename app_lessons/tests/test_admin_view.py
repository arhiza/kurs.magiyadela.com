from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from app_lessons.models import Lesson, Course

USERNAME = 'test'
USER_PASSWORD = 'xdrthnjil'


class TestAdminView(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=USERNAME)
        content_type = ContentType.objects.get_for_model(Course)
        course_permission = Permission.objects.filter(content_type=content_type)
        for perm in course_permission:
            user.user_permissions.add(perm)
        content_type = ContentType.objects.get_for_model(Lesson)
        lesson_permission = Permission.objects.filter(content_type=content_type)
        for perm in lesson_permission:
            user.user_permissions.add(perm)
        course1 = Course.objects.create(name="Курс1", url="kurs1", status=Course.OK, about="Информация о курсе1")
        lesson1 = Lesson.objects.create(name="Урок1", url="urok1", course=course1, info="Секретный текст, недоступный без записи на курс.")
        lesson2 = Lesson.objects.create(name="Урок2", url="urok2", course=course1, info="Второй текст для курса1.")
        course2 = Course.objects.create(name="Курс2", url="kurs2", status=Course.NEW, about="Информация о курсе2")
        lesson3 = Lesson.objects.create(name="Урок3", url="urok3", course=course2, info="Текст, доступный только админу, потому что курс неактивен.")

    def setUp(self):
        user = User.objects.get(username=USERNAME)
        self.client.force_login(user)

    def test_main_page(self):
        response = self.client.get("/")
        course = Course.objects.get(pk=1)
        url1 = course.get_absolute_url()
        course = Course.objects.get(pk=2)
        url2 = course.get_absolute_url()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Курс1")
        self.assertNotContains(response, "Курс2")
        self.assertContains(response, url1)
        self.assertNotContains(response, url2)

    def test_links_to_courses(self):
        course = Course.objects.get(pk=1)
        url1 = course.get_absolute_url()
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Курс1")
        self.assertContains(response, "Информация о курсе1")
        self.assertContains(response, "Урок1")
        lesson = Lesson.objects.get(pk=1)
        url_lesson = lesson.get_absolute_url()
        self.assertContains(response, url_lesson)
        course = Course.objects.get(pk=2)
        url2 = course.get_absolute_url()
        response = self.client.get(url2)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Курс2")
        self.assertContains(response, "Информация о курсе2")
        self.assertContains(response, "Урок3")
        lesson = Lesson.objects.get(pk=3)
        url_lesson = lesson.get_absolute_url()
        self.assertContains(response, url_lesson)

    def test_links_to_lessons(self):
        lesson = Lesson.objects.get(pk=1)
        url1 = lesson.get_absolute_url()
        response = self.client.get(url1)
        course = Course.objects.get(pk=1)
        url_course = course.get_absolute_url()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Урок1")
        self.assertContains(response, "Курс1")
        self.assertContains(response, url_course)
        self.assertContains(response, "Секретный текст")
        lesson = Lesson.objects.get(pk=2)
        url2 = lesson.get_absolute_url()
        self.assertContains(response, url2)
        lesson = Lesson.objects.get(pk=3)
        url3 = lesson.get_absolute_url()
        response = self.client.get(url3)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Текст, доступный только админу")
