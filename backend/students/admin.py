from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("roll_number", "full_name", "department", "year_of_study", "cgpa")
    list_filter = ("department", "year_of_study")
    search_fields = ("roll_number", "full_name", "email")
