from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

def example_mail(to):
    username = to.split("@")[0]
    htmly = get_template("test_mail.html")
    d = {'username': username}
    html_content = htmly.render(d)
    send_mail_from_site("Проверка связи", "Если это сообщение видно, значит, с тегами ничего не получилось.", [to], html_content)


def send_mail_from_site(subject, message, recipient_list, html_content=None, attach=None):
    email = EmailMultiAlternatives(subject=subject, body=message,
                                   from_email=settings.EMAIL_HOST_USER, to=recipient_list)
    if html_content:
        email.attach_alternative(html_content, "text/html")
    if attach:
        email.attach_file(attach)
    email.send()
