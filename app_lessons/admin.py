from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Lesson, Course


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'ordering', 'view_link']
    ordering = ['course', 'ordering']
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
    fields = ['name', 'ordering']
    ordering = ['ordering']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'price', 'view_link']
    inlines = [LessonInLine]

    def view_link(self, obj):
        return mark_safe(
            '<a href="{0}">{1}</a>'.format(
                obj.get_absolute_url(),
                "Посмотреть"
            )
        )
    view_link.allow_tags = True
