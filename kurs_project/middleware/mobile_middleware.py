from django.urls import reverse


class MobileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        info = request.META.get("HTTP_USER_AGENT", "Desktop")
        # print("HTTP_USER_AGENT", info)
        if "Mobile" in info:
            request.is_mobile = True
        else:
            request.is_mobile = False

        my_courses = request.user.to_courses.all() if request.user.is_authenticated else None
        
        if my_courses:
            my_courses_menu = [[course.course.name, course.course.get_absolute_url()] for course in my_courses]
        else:
            my_courses_menu = [["Выберите тут...", reverse("all_courses")]]
        
        request.my_courses_menu = my_courses_menu
        
        main_menu = [["Магия дела", "http://magiyadela.com/", None]]
        if request.user.is_authenticated:
            main_menu.append(["Личный кабинет", reverse("cabinet"), my_courses_menu])
            if request.user.is_staff:
                main_menu.append(["Админка", reverse("admin:index"), None])
            main_menu.append(["Выход", reverse("logout"), None])
            right_menu = [["Выход", reverse("logout")], ["Поменять пароль", reverse("cabinet")]]
        else:
            main_menu.append(["Вход", reverse("login"), None])
            main_menu.append(["Регистрация", reverse("registration"), None])
            right_menu = [["Вход", reverse("login")], ["Регистрация", reverse("registration")]]
        
        request.main_menu = main_menu
        request.right_menu = right_menu
            
        response = self.get_response(request)
        
        return response
        
