from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email')
    search_fields = ('id', 'email')
    list_filter = ('id', 'email')


admin.site.unregister(Group)
