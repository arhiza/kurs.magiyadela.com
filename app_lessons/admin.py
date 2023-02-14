from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Lesson, Course, Category, CoursesForUsers, FilePicture


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'count_of_courses']

    def count_of_courses(self, obj):
        return obj.courses.count()


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    prepopulated_fields = {"url": ("name",)}
    list_display = ['name', 'is_intro', 'course', 'is_child', 'ordering', 'view_link']
    ordering = ['-course', '-ordering']
    list_filter = ['course']

    def view_link(self, obj):
        return mark_safe(
            '<a href="{0}">{1}</a>'.format(
                obj.get_absolute_url(),
                "Посмотреть"
            )
        )
    view_link.allow_tags = True


class LessonInLine(admin.TabularInline):
    model = Lesson
    prepopulated_fields = {"url": ("name",)}
    fields = ['name', 'url', 'is_intro', 'ordering']
    ordering = ['ordering']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    prepopulated_fields = {"url": ("name",)}
    list_display = ['name', 'status', 'category', 'price', 'is_free', 'view_link']
    list_filter = ['category', 'status']
    inlines = [LessonInLine]

    def view_link(self, obj):
        return mark_safe(
            '<a href="{0}">{1}</a>'.format(
                obj.get_absolute_url(),
                "Посмотреть"
            )
        )
    view_link.allow_tags = True


def approve_orders(modeladmin, request, queryset):
    for cfu in queryset:
        cfu.is_active = True
        cfu.save()
approve_orders.short_description = "Активировать выбранные курсы"


@admin.register(CoursesForUsers)
class CoursesForUsersAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_fio', 'course', 'is_active', 'info']
    ordering = ['is_active']
    list_filter = ['course']
    actions = [approve_orders]
    
    @admin.display(description='Кто это')
    def user_fio(self, obj):
        res = []
        if obj.user.first_name:
            res.append(obj.user.first_name)
        if hasattr(obj.user, 'profile'):
            profile = obj.user.profile
            if profile.name_hint:
                res.append(profile.name_hint)
        return " / ".join(res)


@admin.register(FilePicture)
class FilePictureAdmin(admin.ModelAdmin):
    list_display = ['file', 'f_course', 'f_lesson']

    def filename(self, obj):
        return obj.file.name

    def f_course(self, obj):
        return obj.course.first()

    def f_lesson(self, obj):
        return obj.lesson.first()
