from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Lesson, Course, Category, CoursesForUsers


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'count_of_courses']

    def count_of_courses(self, obj):
        return obj.courses.count()


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_intro', 'course', 'ordering', 'view_link']
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
    fields = ['name', 'is_intro', 'ordering']
    ordering = ['ordering']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
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


@admin.register(CoursesForUsers)
class CoursesForUsersAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'is_active', 'info']
