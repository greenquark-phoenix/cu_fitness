from django.contrib import admin
from .models import Schedule, MyList


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('user',)


@admin.register(MyList)
class MyListAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('meals',)
