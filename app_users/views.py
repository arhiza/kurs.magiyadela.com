from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from kurs_project import settings
from .forms import RestorePassword, LoginForm, RegistrationForm, UserUpdateForm
from .models import Profile
from .services import mail_about_new_registration


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


class UserUpdateView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserUpdateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {"form": UserUpdateForm(instance=request.user)}
        return render(request, "app_users/profile.html", context=context)

    def post(self, request, *args, **kwargs):
        form = UserUpdateForm(request.POST, instance=request.user)
        is_ok = False
        if form.is_valid():
            form_data = form.data
            user = request.user
            user.first_name = form_data.get("first_name")
            password = form_data.get("password1")
            if len(password) > 0:
                user.set_password(password)
            user.save()
            is_ok = True
        context = {"form": form, "is_ok": is_ok}
        return render(request, "app_users/profile.html", context=context)


def add_profile(user, password):
    Profile.objects.create(user=user)
    mail_about_new_registration(user, password)


def check_email_address_validity(email_address):
    try:
        validate_email(email_address)
        valid_email = True
    except ValidationError:
        valid_email = False
    return valid_email


def registration_view(request):
    next = request.GET.get("next", None)
    if next:
        redirect_to = next
        link_else = f"{reverse('login')}?next={next}"
    else:
        redirect_to = reverse('all_courses')
        link_else = f"{reverse('login')}"
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            # для регистрации - только логин в виде емейла
            if check_email_address_validity(username):
                password = form.cleaned_data['password']
                user, created = User.objects.get_or_create(username=username)
                if created:  # пользователя с таким логином не было, теперь создался
                    user.email = username
                    user.first_name = form.cleaned_data['fio']
                    user.set_password(password)
                    user.save()
                    add_profile(user, password)
                    login(request, user)
                    return redirect(redirect_to)
                else:
                    form.add_error('login', 'Пользователь с таким емейлом уже существует')
            else:
                form.add_error('login', 'Некорректный адрес электронной почты')
    else:
        form = RegistrationForm()
    return render(request, 'app_users/registration.html', {'form': form, 'link_else': link_else})

def login_view(request):
    next = request.GET.get("next", None)
    if next:
        redirect_to = next
        link_else = f"{reverse('registration')}?next={next}"
    else:
        redirect_to = reverse('all_courses')
        link_else = f"{reverse('registration')}"
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            password = form.cleaned_data['password']
            # для входа годится любой логин, если он уже есть в базе данных
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect(redirect_to)
            else:
                form.add_error('password', 'Пароль не подходит')
                # TODO нужно показать ссылку для восстановления пароля
    else:
        form = LoginForm()
    return render(request, 'app_users/login.html', {'form': form, 'link_else': link_else})


class LogoutView(LogoutView):
    next_page = '/'
