from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import CustomUser, Term, UserTermsAcceptance


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email")
    search_fields = ("id", "email")
    list_filter = ("id", "email")
    exclude = ("groups", "user_permissions", "password")


admin.site.register(Term)
admin.site.register(UserTermsAcceptance)
admin.site.unregister(Group)
