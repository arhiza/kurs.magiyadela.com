from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.mail import send_mail
from django.http import HttpResponse

from .forms import RestorePassword


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
