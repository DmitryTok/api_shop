from django.contrib import admin
from django.contrib.auth.models import Group

from api_shop.admin import CustomModelAdmin
from users.models import CustomUser, Term, UserTermsAcceptance


@admin.register(CustomUser)
class CustomUserAdmin(CustomModelAdmin):
    list_display = ('id', 'email')
    search_fields = ('id', 'email')
    list_filter = ('id', 'email')
    exclude = ('groups', 'user_permissions', 'password')


admin.site.register(Term, CustomModelAdmin)
admin.site.register(UserTermsAcceptance, CustomModelAdmin)
admin.site.unregister(Group)
