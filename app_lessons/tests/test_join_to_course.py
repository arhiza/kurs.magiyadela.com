from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from app_lessons.models import Lesson, Course

USERNAME = 'test'


class TestAnonimFree(TestCase):
    @classmethod
    def setUpTestData(cls):
        course = Course.objects.create(name="Курс1", status=Course.OK, is_free=True, about="Информация о бесплатном курсе")
        Lesson.objects.create(name="Урок1", course=course, info="Текст, видимый без регистрации и записи на курс.")

    def test_no_button(self):
        url1 = reverse('course', args=[1])
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")

    def test_no_post(self):
        url1 = reverse('course', args=[1])
        response = self.client.post(url1, {'buy_course': True})
        self.assertRedirects(response, reverse('course', args=[1]), status_code=302,
                             target_status_code=200)
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")
        url_lesson = reverse('lesson', args=[1])
        self.assertContains(response, url_lesson)


class TestAnonimNotFree(TestCase):
    @classmethod
    def setUpTestData(cls):
        course = Course.objects.create(name="Курс1", status=Course.OK,
                                       about="Информация о платном курсе")
        Lesson.objects.create(name="Урок1", course=course, info="Текст, невидимый без регистрации и записи на курс.")

    def test_no_button(self):
        url1 = reverse('course', args=[1])
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")

    def test_no_post(self):
        url1 = reverse('course', args=[1])
        response = self.client.post(url1, {'buy_course': True})
        self.assertRedirects(response, reverse('course', args=[1]), status_code=302,
                             target_status_code=200)
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")
        url_lesson = reverse('lesson', args=[1])
        self.assertNotContains(response, url_lesson)


class TestAuthFree(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=USERNAME)
        course = Course.objects.create(name="Курс1", status=Course.OK, is_free=True,
                                       about="Информация о бесплатном курсе")
        Lesson.objects.create(name="Урок1", course=course, info="Текст, видимый без регистрации и записи на курс.")

    def setUp(self):
        user = User.objects.get(username=USERNAME)
        self.client.force_login(user)

    def test_button(self):
        url1 = reverse('course', args=[1])
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Записаться на курс")

    def test_post_joined(self):
        url1 = reverse('course', args=[1])
        response = self.client.post(url1, {'buy_course': True})
        self.assertRedirects(response, reverse('course', args=[1]), status_code=302,
                             target_status_code=200)
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")
        url_lesson = reverse('lesson', args=[1])
        self.assertContains(response, url_lesson)


class TestAuthNotFree(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=USERNAME)
        course = Course.objects.create(name="Курс1", status=Course.OK,
                                       about="Информация о платном курсе")
        Lesson.objects.create(name="Урок1", course=course, info="Текст, невидимый без регистрации и записи на курс.")

    def setUp(self):
        user = User.objects.get(username=USERNAME)
        self.client.force_login(user)

    def test_button(self):
        url1 = reverse('course', args=[1])
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Записаться на курс")

    def test_post_no_joined(self):
        url1 = reverse('course', args=[1])
        response = self.client.post(url1, {'buy_course': True})
        self.assertRedirects(response, reverse('course', args=[1]), status_code=302,
                             target_status_code=200)
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")
        url_lesson = reverse('lesson', args=[1])
        self.assertNotContains(response, url_lesson)
