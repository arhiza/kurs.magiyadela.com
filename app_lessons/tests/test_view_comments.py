from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from app_lessons.models import Lesson, Course, Comment, CoursesForUsers


USERNAME = "test"
USERNAME1 = "admin"


class TestViewComments(TestCase):
    @classmethod
    def setUpTestData(cls):
        course1 = Course.objects.create(name="Курс1", url="kurs1", status=Course.OK, about="Информация о курсе1")
        lesson1 = Lesson.objects.create(name="Урок1", url="urok1", course=course1,
                                        info="Секретный текст, недоступный без записи на курс.")
        lesson2 = Lesson.objects.create(name="Урок2", url="urok2", course=course1,
                                        is_intro=True, info="Второй текст для курса1.")

        user = User.objects.create(username=USERNAME)
        user1 = User.objects.create(username=USERNAME1)
        content_type = ContentType.objects.get_for_model(Comment)
        comment_permission = Permission.objects.filter(content_type=content_type)
        for perm in comment_permission:
            user1.user_permissions.add(perm)
        content_type = ContentType.objects.get_for_model(Lesson)
        lesson_permission = Permission.objects.filter(content_type=content_type)
        for perm in lesson_permission:
            user1.user_permissions.add(perm)

        Comment.objects.create(lesson=lesson1, user=user, text_question="ВОПРОС 1", text_answer="ОТВЕТ 1")
        Comment.objects.create(lesson=lesson1, user=user, text_question="ВОПРОС 2",
                               text_answer="ОТВЕТ 2", is_published=True)
        Comment.objects.create(lesson=lesson1, text_question="ВОПРОС 3", text_answer="ОТВЕТ 3", is_published=True)
        Comment.objects.create(lesson=lesson1, text_question="ВОПРОС 4", text_answer="ОТВЕТ 4")

        Comment.objects.create(lesson=lesson2, user=user, text_question="ВОПРОС 1", text_answer="ОТВЕТ 1")
        Comment.objects.create(lesson=lesson2, user=user, text_question="ВОПРОС 2",
                               text_answer="ОТВЕТ 2", is_published=True)
        Comment.objects.create(lesson=lesson2, text_question="ВОПРОС 3", text_answer="ОТВЕТ 3", is_published=True)
        Comment.objects.create(lesson=lesson2, text_question="ВОПРОС 4", text_answer="ОТВЕТ 4")

    def test_anonim_visitor(self):
        lesson = Lesson.objects.get(pk=1)
        response = self.client.get(lesson.get_absolute_url())
        self.assertEqual(response.status_code, 200)  # не видно комментариев, потому что не виден весь урок
        self.assertNotContains(response, "ВОПРОС 1")
        self.assertNotContains(response, "ОТВЕТ 1")
        self.assertNotContains(response, "ВОПРОС 2")
        self.assertNotContains(response, "ОТВЕТ 2")
        self.assertNotContains(response, "ВОПРОС 3")
        self.assertNotContains(response, "ОТВЕТ 3")
        self.assertNotContains(response, "ВОПРОС 4")
        self.assertNotContains(response, "ОТВЕТ 4")
        self.assertNotContains(response, "ответить")

        lesson = Lesson.objects.get(pk=2)
        response = self.client.get(lesson.get_absolute_url())
        self.assertEqual(response.status_code, 200)  # на втором уроке должно быть видно только опубликованное
        self.assertNotContains(response, "ВОПРОС 1")
        self.assertNotContains(response, "ОТВЕТ 1")
        self.assertContains(response, "ВОПРОС 2")
        self.assertContains(response, "ОТВЕТ 2")
        self.assertContains(response, "ВОПРОС 3")
        self.assertContains(response, "ОТВЕТ 3")
        self.assertNotContains(response, "ВОПРОС 4")
        self.assertNotContains(response, "ОТВЕТ 4")
        self.assertNotContains(response, "ответить")

    def test_user_not_at_course(self):
        user = User.objects.get(username=USERNAME)
        self.client.force_login(user)

        lesson = Lesson.objects.get(pk=1)
        response = self.client.get(lesson.get_absolute_url())
        self.assertEqual(response.status_code, 200)  # не видно комментариев, потому что не виден весь урок
        self.assertNotContains(response, "ВОПРОС 1")
        self.assertNotContains(response, "ОТВЕТ 1")
        self.assertNotContains(response, "ВОПРОС 2")
        self.assertNotContains(response, "ОТВЕТ 2")
        self.assertNotContains(response, "ВОПРОС 3")
        self.assertNotContains(response, "ОТВЕТ 3")
        self.assertNotContains(response, "ВОПРОС 4")
        self.assertNotContains(response, "ОТВЕТ 4")
        self.assertNotContains(response, "ответить")

        lesson = Lesson.objects.get(pk=2)
        response = self.client.get(lesson.get_absolute_url())
        self.assertEqual(response.status_code, 200)  # на втором уроке должно быть видно опубликованное и свое
        self.assertContains(response, "ВОПРОС 1")
        self.assertContains(response, "ОТВЕТ 1")
        self.assertContains(response, "ВОПРОС 2")
        self.assertContains(response, "ОТВЕТ 2")
        self.assertContains(response, "ВОПРОС 3")
        self.assertContains(response, "ОТВЕТ 3")
        self.assertNotContains(response, "ВОПРОС 4")
        self.assertNotContains(response, "ОТВЕТ 4")
        self.assertNotContains(response, "ответить")

    def test_user_at_course(self):
        user = User.objects.get(username=USERNAME)
        self.client.force_login(user)
        course = Course.objects.get(pk=1)
        CoursesForUsers.objects.create(user=user, course=course, is_active=True)

        lesson = Lesson.objects.get(pk=1)
        response = self.client.get(lesson.get_absolute_url())
        self.assertEqual(response.status_code, 200)  # на первом уроке видны свои комментарии и любые опубликованные
        self.assertContains(response, "ВОПРОС 1")
        self.assertContains(response, "ОТВЕТ 1")
        self.assertContains(response, "ВОПРОС 2")
        self.assertContains(response, "ОТВЕТ 2")
        self.assertContains(response, "ВОПРОС 3")
        self.assertContains(response, "ОТВЕТ 3")
        self.assertNotContains(response, "ВОПРОС 4")
        self.assertNotContains(response, "ОТВЕТ 4")
        self.assertNotContains(response, "ответить")

        lesson = Lesson.objects.get(pk=2)
        response = self.client.get(lesson.get_absolute_url())
        self.assertEqual(response.status_code, 200)  # на втором уроке - точно так же
        self.assertContains(response, "ВОПРОС 1")
        self.assertContains(response, "ОТВЕТ 1")
        self.assertContains(response, "ВОПРОС 2")
        self.assertContains(response, "ОТВЕТ 2")
        self.assertContains(response, "ВОПРОС 3")
        self.assertContains(response, "ОТВЕТ 3")
        self.assertNotContains(response, "ВОПРОС 4")
        self.assertNotContains(response, "ОТВЕТ 4")
        self.assertNotContains(response, "ответить")

    def test_admin_view(self):
        user = User.objects.get(username=USERNAME1)
        self.client.force_login(user)

        lesson = Lesson.objects.get(pk=1)
        response = self.client.get(lesson.get_absolute_url())
        self.assertEqual(response.status_code, 200)  # админу видны все комментарии
        self.assertContains(response, "ВОПРОС 1")
        self.assertContains(response, "ОТВЕТ 1")
        self.assertContains(response, "ВОПРОС 2")
        self.assertContains(response, "ОТВЕТ 2")
        self.assertContains(response, "ВОПРОС 3")
        self.assertContains(response, "ОТВЕТ 3")
        self.assertContains(response, "ВОПРОС 4")
        self.assertContains(response, "ОТВЕТ 4")
        self.assertContains(response, "ответить")

        lesson = Lesson.objects.get(pk=2)
        response = self.client.get(lesson.get_absolute_url())
        self.assertEqual(response.status_code, 200)  # админу видны все комментарии
        self.assertContains(response, "ВОПРОС 1")
        self.assertContains(response, "ОТВЕТ 1")
        self.assertContains(response, "ВОПРОС 2")
        self.assertContains(response, "ОТВЕТ 2")
        self.assertContains(response, "ВОПРОС 3")
        self.assertContains(response, "ОТВЕТ 3")
        self.assertContains(response, "ВОПРОС 4")
        self.assertContains(response, "ОТВЕТ 4")
        self.assertContains(response, "ответить")
