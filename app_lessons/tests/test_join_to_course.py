from django.contrib.auth.models import User
from django.test import TestCase

from app_lessons.models import Lesson, Course

USERNAME = 'test'


class TestAnonimFree(TestCase):
    @classmethod
    def setUpTestData(cls):
        course = Course.objects.create(name="Курс1", url="kurs1", status=Course.OK,
                                       is_free=True, about="Информация о бесплатном курсе")
        Lesson.objects.create(name="Урок1", url="urok1", course=course,
                              info="Текст, видимый без регистрации и записи на курс.")
        course2 = Course.objects.create(name="Курс2", url="kurs2", status=Course.PROMO,
                                       is_free=True, about="Информация о бесплатном курсе")
        Lesson.objects.create(name="Урок2", url="urok2", course=course2,
                              info="Текст, видимый без регистрации и записи на курс.")

    def test_no_button(self):
        course = Course.objects.get(pk=1)
        url1 = course.get_absolute_url()
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")

    def test_no_post(self):
        course = Course.objects.get(pk=1)
        url1 = course.get_absolute_url()
        response = self.client.post(url1, {'buy_course': True, 'course_id': 1})
        self.assertRedirects(response, url1, status_code=302,
                             target_status_code=200)
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")
        lesson = Lesson.objects.get(pk=1)
        url_lesson = lesson.get_absolute_url()
        self.assertContains(response, url_lesson)
        # TODO никаких отправленных писем

    def test_no_button_2(self):
        course = Course.objects.get(pk=2)
        url1 = course.get_absolute_url()
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")

    def test_no_post_2(self):
        course = Course.objects.get(pk=2)
        url1 = course.get_absolute_url()
        response = self.client.post(url1, {'buy_course': True, 'course_id': 1})
        self.assertRedirects(response, url1, status_code=302,
                             target_status_code=200)
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")
        lesson = Lesson.objects.get(pk=2)
        url_lesson = lesson.get_absolute_url()
        self.assertContains(response, url_lesson)


class TestAnonimNotFree(TestCase):
    @classmethod
    def setUpTestData(cls):
        course = Course.objects.create(name="Курс1", url="kurs1", status=Course.OK,
                                       about="Информация о платном курсе")
        Lesson.objects.create(name="Урок1", url="urok1", course=course,
                              info="Текст, невидимый без регистрации и записи на курс.")
        course2 = Course.objects.create(name="Курс2", url="kurs2", status=Course.PROMO,
                                       about="Информация о платном курсе")
        Lesson.objects.create(name="Урок2", url="urok2", course=course2,
                              info="Текст, невидимый без регистрации и записи на курс.")

    def test_no_button(self):
        course = Course.objects.get(pk=1)
        url1 = course.get_absolute_url()
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")

    def test_no_post(self):
        course = Course.objects.get(pk=1)
        url1 = course.get_absolute_url()
        response = self.client.post(url1, {'buy_course': True, 'course_id': 1})
        self.assertRedirects(response, url1, status_code=302,
                             target_status_code=200)
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")
        lesson = Lesson.objects.get(pk=1)
        url_lesson = lesson.get_absolute_url()
        self.assertNotContains(response, url_lesson)
        # TODO никаких отправленных писем

    def test_no_button_2(self):
        course = Course.objects.get(pk=2)
        url1 = course.get_absolute_url()
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")

    def test_no_post_2(self):
        course = Course.objects.get(pk=2)
        url1 = course.get_absolute_url()
        response = self.client.post(url1, {'buy_course': True, 'course_id': 2})
        self.assertRedirects(response, url1, status_code=302,
                             target_status_code=200)
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")
        lesson = Lesson.objects.get(pk=1)
        url_lesson = lesson.get_absolute_url()
        self.assertNotContains(response, url_lesson)


class TestAuthFree(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username=USERNAME)
        course = Course.objects.create(name="Курс1", url="kurs1", status=Course.OK, is_free=True,
                                       about="Информация о бесплатном курсе")
        Lesson.objects.create(name="Урок1", url="urok1", course=course,
                              info="Текст, видимый без регистрации и записи на курс.")
        course2 = Course.objects.create(name="Курс2", url="kurs2", status=Course.PROMO, is_free=True,
                                       about="Информация о бесплатном курсе")
        Lesson.objects.create(name="Урок2", url="urok2", course=course2,
                              info="Текст, видимый без регистрации и записи на курс.")

    def setUp(self):
        user = User.objects.get(username=USERNAME)
        self.client.force_login(user)

    def test_button(self):
        course = Course.objects.get(pk=1)
        url1 = course.get_absolute_url()
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Отправить заявку на курс")

    def test_post_joined(self):
        course = Course.objects.get(pk=1)
        url1 = course.get_absolute_url()
        response = self.client.post(url1, {'buy_course': True, 'course_id': 1})
        self.assertRedirects(response, url1, status_code=302,
                             target_status_code=200)
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")
        lesson = Lesson.objects.get(pk=1)
        url_lesson = lesson.get_absolute_url()
        self.assertContains(response, url_lesson)
        # TODO никаких отправленных писем

    def test_button_2(self):
        course = Course.objects.get(pk=2)
        url1 = course.get_absolute_url()
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Отправить заявку на курс")

    def test_post_joined_2(self):
        course = Course.objects.get(pk=2)
        url1 = course.get_absolute_url()
        response = self.client.post(url1, {'buy_course': True, 'course_id': 2})
        self.assertRedirects(response, url1, status_code=302,
                             target_status_code=200)
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")
        lesson = Lesson.objects.get(pk=2)
        url_lesson = lesson.get_absolute_url()
        self.assertContains(response, url_lesson)


class TestAuthNotFree(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username=USERNAME)
        course = Course.objects.create(name="Курс1", url="kurs1", status=Course.OK,
                                       about="Информация о платном курсе")
        Lesson.objects.create(name="Урок1", url="urok1", course=course,
                              info="Текст, невидимый без регистрации и записи на курс.")
        course2 = Course.objects.create(name="Курс2", url="kurs2", status=Course.PROMO,
                                       about="Информация о платном курсе")
        Lesson.objects.create(name="Урок2", url="urok2", course=course2,
                              info="Текст, невидимый без регистрации и записи на курс.")

    def setUp(self):
        user = User.objects.get(username=USERNAME)
        self.client.force_login(user)

    def test_button(self):
        course = Course.objects.get(pk=1)
        url1 = course.get_absolute_url()
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Отправить заявку на курс")

    def test_post_no_joined(self):
        course = Course.objects.get(pk=1)
        url1 = course.get_absolute_url()
        response = self.client.post(url1, {'buy_course': True, 'course_id': 1})
        self.assertRedirects(response, url1, status_code=302,
                             target_status_code=200)
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")
        lesson = Lesson.objects.get(pk=1)
        url_lesson = lesson.get_absolute_url()
        self.assertNotContains(response, url_lesson)
        # TODO должно отправиться письмо на почту админу

    def test_button_2(self):
        course = Course.objects.get(pk=2)
        url1 = course.get_absolute_url()
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Отправить заявку на курс")

    def test_post_no_joined_2(self):
        course = Course.objects.get(pk=2)
        url1 = course.get_absolute_url()
        response = self.client.post(url1, {'buy_course': True, 'course_id': 2})
        self.assertRedirects(response, url1, status_code=302,
                             target_status_code=200)
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Записаться на курс")
        lesson = Lesson.objects.get(pk=1)
        url_lesson = lesson.get_absolute_url()
        self.assertNotContains(response, url_lesson)
