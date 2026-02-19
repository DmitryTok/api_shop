from django.contrib import admin
from profiles.models import Profile


@admin.register(Profile)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user__email')
    search_fields = ('id', 'user__email')
    list_filter = ('id', 'user__email')
