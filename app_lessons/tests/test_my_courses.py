from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from app_lessons.models import Lesson, Course, CoursesForUsers

USERNAME = 'test'


class TestLinkToMyCourse(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=USERNAME)
        course = Course.objects.create(name="Курс1", url="kurs1", status=Course.OK,
                                       about="Информация о платном курсе")
        Lesson.objects.create(name="Урок1", url="urok1", course=course,
                              info="Текст, невидимый без регистрации и записи на курс.")
        CoursesForUsers.objects.create(course=course, user=user, is_active=True)
        course = Course.objects.create(name="Курс2", url="kurs2", status=Course.PROMO,
                                       about="Новый курс")
        CoursesForUsers.objects.create(course=course, user=user, is_active=True)

    def setUp(self):
        user = User.objects.get(username=USERNAME)
        self.client.force_login(user)

    def test_link_seen_from_everywhere(self):
        course = Course.objects.get(pk=1)
        url_need = course.get_absolute_url()
        course2 = Course.objects.get(pk=2)
        url_need2 = course2.get_absolute_url()
        url_cur = reverse("cabinet")
        response = self.client.get(url_cur)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, course.name)
        self.assertContains(response, url_need)
        self.assertContains(response, course2.name)
        self.assertContains(response, url_need2)

        response = self.client.get(url_cur, HTTP_USER_AGENT='...Mobile...')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, course.name)
        self.assertContains(response, url_need)
        self.assertContains(response, course2.name)
        self.assertContains(response, url_need2)

