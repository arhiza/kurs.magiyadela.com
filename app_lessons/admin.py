from django.contrib import admin

from .models import Lesson, Course


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'ordering']
    ordering = ['course', 'ordering']
    list_filter = ['course']


class LessonInLine(admin.TabularInline):
    model = Lesson
    fields = ['name', 'ordering']
    ordering = ['ordering']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInLine]
