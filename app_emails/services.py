from django.conf import settings
# from django.test import override_settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.urls import reverse

from app_users.models import SiteSettings


def mail_about_answered_comment(comm):
    txt_question = comm.text_question
    txt_answer = comm.text_answer
    lesson = comm.lesson
    title = f"Комментарий к уроку {lesson.name.upper()}"
    htmly = get_template("app_emails/mail_about_answered_comment.html")  # TODO убрать хардкод
    d = {"txt_question": txt_question, "txt_answer": txt_answer,
         "lesson_url": "https://kurs.magiyadela.com" + lesson.get_absolute_url(), "lesson": lesson}
    html_content = htmly.render(d)
    adr = comm.adresates
    if adr:
        for to in adr:  # TODO встроить проверку, сколько времени заняла рассылка
            send_mail_from_site(title, html_content, [to], html_content)


def mail_about_new_comment(request, comm):
    txt = comm.text_question
    lesson = comm.lesson
    title = f"Новый ВОПРОС к уроку {lesson.name.upper()}"
    htmly = get_template("app_emails/mail_about_new_comment.html")
    d = {"txt": txt, "lesson_url": request.build_absolute_uri(lesson.get_absolute_url()),
         "lesson": lesson,
         "admin_url": request.build_absolute_uri(reverse("admin:app_lessons_comment_change", args=[comm.pk]))}
    html_content = htmly.render(d)
    to = SiteSettings.objects.filter(key="order_mail").first()  # TODO comment_mail ?
    if to:
        send_mail_from_site(title, html_content, [to.value], html_content)
    else:
        print("Настройка для отправки почты не найдена", title, html_content)


def mail_about_new_order(cfu):
    # cfu: CoursesForUsers
    usermail = cfu.user.email
    if not usermail:
        usermail = cfu.user.username
    coursename = cfu.course.name
    title = f"ЗАЯВКА НА КУРС {coursename.upper()}"
    htmly = get_template("app_emails/mail_about_new_order.html")
    d = {"usermail": usermail, "coursename": coursename}
    html_content = htmly.render(d)
    to = SiteSettings.objects.filter(key="order_mail").first()
    if to:
        send_mail_from_site(title, html_content, [to.value], html_content)
    else:
        print("Настройка для отправки почты не найдена", title, html_content)


def mail_about_confirm(request, user):
    title = "КУРСЫ МАГИИ ДЕЛА: Подтверждение емейла"
    htmly = get_template("app_emails/mail_about_confirm.html")
    params = user.profile.get_new_params_for_confirm
    link_confirm = request.build_absolute_uri(reverse('confirm')) + params
    d = {"name": user.first_name, "link_confirm": link_confirm}
    html_content = htmly.render(d)
    send_mail_from_site(title, html_content, [user.email], html_content)


def mail_about_new_registration(request, user, password):
    title = "Регистрация на Курсах от Магии дела"
    htmly = get_template("app_emails/mail_about_registration.html")
    params = user.profile.get_new_params_for_confirm
    link_confirm = request.build_absolute_uri(reverse('confirm')) + params
    d = {"usermail": user.username, "password": password, "link_confirm": link_confirm}
    html_content = htmly.render(d)
    send_mail_from_site(title, html_content, [user.email], html_content)


def mail_about_approved_order(cfu):
    course_name = cfu.course.name
    title = f"Открыт доступ к материалам курса {course_name}"
    htmly = get_template("app_emails/mail_about_approved_order.html")
    link = "https://kurs.magiyadela.com" + cfu.course.get_absolute_url()
    d = {"fio": cfu.user.first_name, "course_name": course_name, "link": link}
    html_content = htmly.render(d)
    send_mail_from_site(title, html_content, [cfu.user.email], html_content)


def example_mail(to):
    username = to.split("@")[0]
    htmly = get_template("app_emails/test_mail.html")
    d = {'username': username}
    html_content = htmly.render(d)
    send_mail_from_site("Проверка связи", "Если это сообщение видно, значит, с тегами ничего не получилось.",
                        [to], html_content)


# @override_settings(DEBUG=False)
def send_mail_from_site(subject, message, recipient_list, html_content=None, attach=None):
    if settings.DEBUG:
        print("Письмо не отправлено, ибо включен дебаг:")
        print(subject, recipient_list)
        print(message)
        print(html_content)
    else:
        try:
            email = EmailMultiAlternatives(subject=subject, body=message,
                                           from_email=settings.EMAIL_HOST_USER, to=recipient_list)
            if html_content:
                email.attach_alternative(html_content, "text/html")
            if attach:
                email.attach_file(attach)
            email.send()
        except:
            print("Письмо не отправлено - ЧТО-ТО ПОШЛО НЕ ТАК:")
            print(subject, recipient_list)
            print(message)
            print(html_content)
