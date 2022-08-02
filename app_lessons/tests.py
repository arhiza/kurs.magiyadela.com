from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from app_lessons.models import Lesson, Course


class TestEmptyDB(TestCase):
    def test_main_url_exists(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class TestAnonimVisitor(TestCase):
    @classmethod
    def setUpTestData(cls):
        course1 = Course.objects.create(name="Курс1", status=Course.OK, about="Информация о курсе1")
        lesson1 = Lesson.objects.create(name="Урок1", course=course1, info="Секретный текст, недоступный без записи на курс.")
        lesson2 = Lesson.objects.create(name="Урок2", course=course1, info="Второй текст для курса1.")
        course2 = Course.objects.create(name="Курс2", status=Course.NEW, about="Информация о курсе2")
        lesson3 = Lesson.objects.create(name="Урок3", course=course2, info="Текст, доступный только админу, потому что курс неактивен.")

    def test_main_page(self):
        response = self.client.get("/")
        url1 = reverse('course', args=[1])
        url2 = reverse('course', args=[2])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Курс1")
        self.assertNotContains(response, "Курс2")
        self.assertContains(response, url1)
        self.assertNotContains(response, url2)

    def test_links_to_courses(self):
        url1 = reverse('course', args=[1])
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Курс1")
        self.assertContains(response, "Информация о курсе1")
        self.assertContains(response, "Урок1")
        url_lesson = reverse('lesson', args=[1])
        self.assertNotContains(response, url_lesson)
        url2 = reverse('course', args=[2])
        response = self.client.get(url2)
        self.assertEqual(response.status_code, 404)

    def test_links_to_lessons(self):
        url1 = reverse('lesson', args=[1])
        response = self.client.get(url1)
        url_course = reverse('course', args=[1])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Урок1")
        self.assertContains(response, "Курс1")
        self.assertContains(response, url_course)
        self.assertNotContains(response, "Секретный текст")
        url2 = reverse('lesson', args=[2])
        self.assertNotContains(response, url2)
        url3 = reverse('lesson', args=[3])
        response = self.client.get(url3)
        self.assertEqual(response.status_code, 404)


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
        course1 = Course.objects.create(name="Курс1", status=Course.OK, about="Информация о курсе1")
        lesson1 = Lesson.objects.create(name="Урок1", course=course1, info="Секретный текст, недоступный без записи на курс.")
        lesson2 = Lesson.objects.create(name="Урок2", course=course1, info="Второй текст для курса1.")
        course2 = Course.objects.create(name="Курс2", status=Course.NEW, about="Информация о курсе2")
        lesson3 = Lesson.objects.create(name="Урок3", course=course2, info="Текст, доступный только админу, потому что курс неактивен.")

    def setUp(self):
        user = User.objects.get(username=USERNAME)
        self.client.force_login(user)

    def test_main_page(self):
        response = self.client.get("/")
        url1 = reverse('course', args=[1])
        url2 = reverse('course', args=[2])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Курс1")
        self.assertNotContains(response, "Курс2")
        self.assertContains(response, url1)
        self.assertNotContains(response, url2)

    def test_links_to_courses(self):
        url1 = reverse('course', args=[1])
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Курс1")
        self.assertContains(response, "Информация о курсе1")
        self.assertContains(response, "Урок1")
        url_lesson = reverse('lesson', args=[1])
        self.assertContains(response, url_lesson)
        url2 = reverse('course', args=[2])
        response = self.client.get(url2)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Курс2")
        self.assertContains(response, "Информация о курсе2")
        self.assertContains(response, "Урок3")
        url_lesson = reverse('lesson', args=[3])
        self.assertContains(response, url_lesson)

    def test_links_to_lessons(self):
        url1 = reverse('lesson', args=[1])
        response = self.client.get(url1)
        url_course = reverse('course', args=[1])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Урок1")
        self.assertContains(response, "Курс1")
        self.assertContains(response, url_course)
        self.assertContains(response, "Секретный текст")
        url2 = reverse('lesson', args=[2])
        self.assertContains(response, url2)
        url3 = reverse('lesson', args=[3])
        response = self.client.get(url3)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Текст, доступный только админу")
