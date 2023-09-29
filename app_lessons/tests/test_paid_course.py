from django.test import TestCase

from django.contrib.auth.models import User

from app_lessons.models import Course, Lesson, CoursesForUsers

USERNAME = 'test'


class TestPaidCourse(TestCase):
    @classmethod
    def setUpTestData(cls):
        course1 = Course.objects.create(name="Курс1", url="test1", status=Course.OK, about="Информация о курсе")
        Lesson.objects.create(name="Урок1", url="urok1", course=course1, info="Первый текст урока")
        Lesson.objects.create(name="Урок2", url="urok2", course=course1, info="Второй урок курса")
        user = User.objects.create(username=USERNAME)
        CoursesForUsers.objects.create(course=course1, user=user, is_active=True)

    def setUp(self):
        user = User.objects.get(username=USERNAME)
        self.client.force_login(user)

    def test_links_to_courses(self):
        course1 = Course.objects.get(pk=1)
        url1 = course1.get_absolute_url()
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, course1.name)
        self.assertContains(response, course1.about)
        lesson1 = Lesson.objects.get(pk=1)
        self.assertContains(response, lesson1.name)
        self.assertContains(response, lesson1.get_absolute_url())

    def test_links_to_lessons(self):
        lesson1 = Lesson.objects.get(pk=1)
        response = self.client.get(lesson1.get_absolute_url())
        course1 = Course.objects.get(pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, lesson1.name)
        self.assertContains(response, lesson1.info)
        self.assertContains(response, course1.name)
        self.assertContains(response, course1.get_absolute_url())
        lesson2 = Lesson.objects.get(pk=2)
        self.assertContains(response, "Следующий урок")
        self.assertContains(response, lesson2.get_absolute_url())

        response = self.client.get(lesson2.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, lesson2.name)
        self.assertContains(response, lesson2.info)
        self.assertContains(response, course1.name)
        self.assertContains(response, course1.get_absolute_url())
        self.assertContains(response, "Предыдущий урок")
        self.assertContains(response, lesson1.get_absolute_url())


class TestPaidPROMOCourse(TestCase):
    @classmethod
    def setUpTestData(cls):
        course1 = Course.objects.create(name="Курс1", url="test1", status=Course.PROMO, about="Информация о курсе")
        Lesson.objects.create(name="Урок1", url="urok1", course=course1, info="Первый текст урока")
        Lesson.objects.create(name="Урок2", url="urok2", course=course1, info="Второй урок курса")
        user = User.objects.create(username=USERNAME)
        CoursesForUsers.objects.create(course=course1, user=user, is_active=True)

    def setUp(self):
        user = User.objects.get(username=USERNAME)
        self.client.force_login(user)

    def test_links_to_courses(self):
        course1 = Course.objects.get(pk=1)
        url1 = course1.get_absolute_url()
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, course1.name)
        self.assertContains(response, course1.about)
        lesson1 = Lesson.objects.get(pk=1)
        self.assertContains(response, lesson1.name)
        self.assertContains(response, lesson1.get_absolute_url())

    def test_links_to_lessons(self):
        lesson1 = Lesson.objects.get(pk=1)
        response = self.client.get(lesson1.get_absolute_url())
        course1 = Course.objects.get(pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, lesson1.name)
        self.assertContains(response, lesson1.info)
        self.assertContains(response, course1.name)
        self.assertContains(response, course1.get_absolute_url())
        lesson2 = Lesson.objects.get(pk=2)
        self.assertContains(response, "Следующий урок")
        self.assertContains(response, lesson2.get_absolute_url())

        response = self.client.get(lesson2.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, lesson2.name)
        self.assertContains(response, lesson2.info)
        self.assertContains(response, course1.name)
        self.assertContains(response, course1.get_absolute_url())
        self.assertContains(response, "Предыдущий урок")
        self.assertContains(response, lesson1.get_absolute_url())
