from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import reverse

from .forms import RestorePassword, LoginForm


def restore_password(request):
    if request.method == "POST":
        form = RestorePassword(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data["email"]
            new_password = User.objects.make_random_password()
            current_user, created = User.objects.get_or_create(email=user_email)
            if created:
                current_user.username = user_email
            current_user.set_password(new_password)
            current_user.save()
            send_mail(subject="Восстановление пароля",
                      message=new_password,
                      from_email="admin@company.com",
                      recipient_list=[user_email])
            return HttpResponse('Письмо с новым паролем отправлено')
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
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect(reverse('all_courses'))
            user, created = User.objects.get_or_create(username=username)
            if created:  # пользователя с таким логином не было, теперь создался
                if check_email_address_validity(username):
                    user.email = username
                user.set_password(password)
                user.save()
                login(request, user)
                return redirect(reverse('all_courses'))
            else:
                # print("пользователь есть, пароль не подходит")
                form.add_error('__all__', 'Проверьте правильность введенных данных')
                if user.email == username:
                    # TODO нужно показать ссылку для восстановления пароля
                    pass
    else:
        form = LoginForm()
    return render(request, 'app_users/login.html', {'form': form})


class LogoutView(LogoutView):
    next_page = '/'
