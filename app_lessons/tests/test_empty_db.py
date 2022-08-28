from django.test import TestCase
from django.urls import reverse

from app_lessons.models import Course, Lesson


class TestEmptyDB(TestCase):
    def test_main_url_exists(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'kurs/')


class TestNoUrl(TestCase):
    def test_no_url_course(self):
        course1 = Course.objects.create(name="Курс1", status=Course.OK, about="Информация о курсе")
        url = course1.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/")
        self.assertNotContains(response, url)

    def test_no_url_lesson(self):
        course1 = Course.objects.create(name="Курс1", url="test1", status=Course.OK, about="Информация о курсе")
        lesson1 = Lesson.objects.create(name="Урок1", course=course1, info="Первый текст урока")
        response = self.client.get(course1.get_absolute_url())
        self.assertNotContains(response, "Урок1")
        response = self.client.get(lesson1.get_absolute_url())
        self.assertEqual(response.status_code, 404)
