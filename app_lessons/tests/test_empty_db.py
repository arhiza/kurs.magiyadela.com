from django.test import TestCase
from django.urls import reverse


class TestEmptyDB(TestCase):
    def test_main_url_exists(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_none_courses(self):
        url1 = reverse('course', args=[1])
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 404)

    def test_none_lessons(self):
        url1 = reverse('lesson', args=[1])
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 404)
