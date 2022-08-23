from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import reverse

from kurs_project import settings
from .forms import RestorePassword, LoginForm


def restore_password(request):
    if request.method == "POST":
        form = RestorePassword(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data["email"]
            new_password = User.objects.make_random_password()
            # todo лучше не создавать пользователя, а сообщать, что такого нет, если его нет
            current_user, created = User.objects.get_or_create(email=user_email)
            if created:
                current_user.username = user_email
            # todo и не сбрасывать пароль, а сохранять закешированный в отдельном поле
            current_user.set_password(new_password)
            current_user.save()
            try:  # todo тут должно быть нормальное содержимое, а не только пароль
                send_mail(subject="Восстановление пароля",
                      message=f'''Новые данные для входа в систему:
логин: {user_email}
пароль: {new_password}''',
                      from_email=settings.EMAIL_HOST_USER,
                      recipient_list=[user_email])
                return HttpResponse('Письмо с новым паролем отправлено')
            except:
                return HttpResponse('ОШИБКА: отправить письмо не удалось')
    restore_password_form = RestorePassword()
    context = {
        'form': restore_password_form
    }
    return render(request, 'app_users/restore_password.html', context=context)


def check_email_address_validity(email_address):
    try:
        validate_email(email_address)
        valid_email = True
    except ValidationError:
        valid_email = False
    return valid_email


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            password = form.cleaned_data['password']
            # для входа годится любой логин, если он уже есть в базе данных
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect(reverse('all_courses'))
            # для регистрации - только логин в виде емейла
            if check_email_address_validity(username):
                user, created = User.objects.get_or_create(username=username)
                if created:  # пользователя с таким логином не было, теперь создался
                    user.email = username
                    user.set_password(password)
                    user.save()
                    login(request, user)
                    return redirect(reverse('all_courses'))
                else:
                    form.add_error('password', 'Пароль не подходит')
                    # TODO нужно показать ссылку для восстановления пароля
            else:
                form.add_error('login', 'Некорректный адрес электронной почты')
    else:
        form = LoginForm()
    return render(request, 'app_users/login.html', {'form': form})


class LogoutView(LogoutView):
    next_page = '/'
