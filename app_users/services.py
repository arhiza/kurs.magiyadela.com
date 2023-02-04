from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from app_lessons.models import CoursesForUsers
from app_users.models import SiteSettings


def mail_about_new_order(cfu):
    usermail = cfu.user.email
    if not usermail:
        usermail = cfu.user.username
    coursename = cfu.course.name
    title = f"ЗАЯВКА НА КУРС {coursename.upper()}"
    htmly = get_template("emails/mail_about_new_order.html")
    d = {"usermail": usermail, "coursename": coursename}
    html_content = htmly.render(d)
    to = SiteSettings.objects.filter(key="order_mail").first()
    if to:
        send_mail_from_site(title, html_content, [to.value], html_content)
    else:
        print("Настройка для отправки почты не найдена", title, html_content)


def example_mail(to):
    username = to.split("@")[0]
    htmly = get_template("test_mail.html")
    d = {'username': username}
    html_content = htmly.render(d)
    send_mail_from_site("Проверка связи", "Если это сообщение видно, значит, с тегами ничего не получилось.", [to], html_content)


def send_mail_from_site(subject, message, recipient_list, html_content=None, attach=None):
    if settings.DEBUG:
        print("Письмо не отправлено, ибо включен дебаг:")
        print(subject, recipient_list)
        print(message)
    else:
        email = EmailMultiAlternatives(subject=subject, body=message,
                                       from_email=settings.EMAIL_HOST_USER, to=recipient_list)
        if html_content:
            email.attach_alternative(html_content, "text/html")
        if attach:
            email.attach_file(attach)
        email.send()
