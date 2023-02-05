from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class TestRegistration(TestCase):
    def test_registration_url_exists(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)

    def test_login_uses_correct_template(self):
        response = self.client.get(reverse('registration'))
        self.assertTemplateUsed(response, 'app_users/registration.html')

    def test_post_registration_correct(self):
        response = self.client.post(reverse('registration'), {'login': 'test@email.ururu',
                                                          'fio': 'Тестовый юзер',
                                                          'password': 'xdrthnjil'})
        count_after = User.objects.count()
        self.assertEqual(count_after, 1)  # в базе появился один пользователь
        user = authenticate(username='test@email.ururu', password='xdrthnjil')
        self.assertNotEqual(user, None)  # залогиниться этим пользователем можно
        self.assertEqual(user.email, 'test@email.ururu')  # email тоже прописался
        self.assertEqual(user.first_name, 'Тестовый юзер')
        # все успешно и редирект куда надо
        self.assertRedirects(response, '/', status_code=302, target_status_code=200)

    def test_post_registration_not_correct(self):  # невалидная форма - логин не емейл
        response = self.client.post(reverse('registration'), {'login': 'test1',
                                                          'fio': 'TEST',
                                                          'password': 'xdrthnjil'})
        self.assertEqual(response.status_code, 200)  # та же страница с формой
        self.assertFormError(response, 'form', 'login', 'Некорректный адрес электронной почты')
        count_after = User.objects.count()
        self.assertEqual(count_after, 0)


USERNAME_1 = 'test1'
USERNAME_2 = 'test@test.com'
PASSWORD = 'xdrthnjil'
FAIL_PASS = 'fail_password'

class TestAuthentication(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=USERNAME_1)
        user.set_password(PASSWORD)
        user.save()
        user = User.objects.create(username=USERNAME_2)
        user.set_password(PASSWORD)
        user.save()

    def test_authentication_register_correct(self):
        response = self.client.post(reverse('login'), {'login': USERNAME_1,
                                                        'password': PASSWORD})
        self.assertRedirects(response, '/', status_code=302, target_status_code=200)
        self.assertEqual(response.client.session.get('_auth_user_id'), '1')  # залогиненность
        response = self.client.post(reverse('login'), {'login': USERNAME_2,
                                                        'password': PASSWORD})
        self.assertRedirects(response, '/', status_code=302, target_status_code=200)
        self.assertEqual(response.client.session.get('_auth_user_id'), '2')  # залогиненность

    def test_authentication_register_not_correct(self):
        response = self.client.post(reverse('login'), {'login': USERNAME_1,
                                                        'password': FAIL_PASS})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password', 'Пароль не подходит')
        self.assertEqual(response.client.session.get('_auth_user_id'), None)
        response = self.client.post(reverse('login'), {'login': USERNAME_2,
                                                        'password': FAIL_PASS})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password', 'Пароль не подходит')
        # TODO тут еще надо будет проверить наличие ссылки на сброс пароля через емейл
        self.assertEqual(response.client.session.get('_auth_user_id'), None)

    def test_logout_url_exists(self):
        user = User.objects.get(username=USERNAME_1)
        self.client.force_login(user)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, '/', status_code=302, target_status_code=200)
        self.assertEqual(response.client.session.get('_auth_user_id'), None)
