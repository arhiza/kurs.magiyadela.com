from django.test import TestCase

from django.contrib.auth.models import User
from django.urls import reverse

from app_lessons.models import Course, Lesson, CoursesForUsers

USERNAME = 'test'
USER_PASSWORD = 'xdrthnjil'


class TestPaidCourse(TestCase):
    @classmethod
    def setUpTestData(cls):
        course1 = Course.objects.create(name="Курс1", status=Course.OK, about="Информация о курсе")
        lesson1 = Lesson.objects.create(name="Урок1", course=course1, info="Первый текст урока")
        lesson2 = Lesson.objects.create(name="Урок2", course=course1, info="Второй урок курса")
        user = User.objects.create(username=USERNAME)
        CoursesForUsers.objects.create(course=course1, user=user, is_active=True)

    def setUp(self):
        user = User.objects.get(username=USERNAME)
        self.client.force_login(user)

    def test_main_page(self):
        response = self.client.get("/")
        url1 = reverse('course', args=[1])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Курс1")
        self.assertContains(response, url1)

    def test_links_to_courses(self):
        url1 = reverse('course', args=[1])
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Курс1")
        self.assertContains(response, "Информация о курсе")
        self.assertContains(response, "Урок1")
        url_lesson = reverse('lesson', args=[1])
        self.assertContains(response, url_lesson)

    def test_links_to_lessons(self):
        url1 = reverse('lesson', args=[1])
        response = self.client.get(url1)
        url_course = reverse('course', args=[1])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Урок1")
        self.assertContains(response, "Курс1")
        self.assertContains(response, url_course)
        self.assertContains(response, "Первый текст урока")
        url2 = reverse('lesson', args=[2])
        self.assertContains(response, url2)

