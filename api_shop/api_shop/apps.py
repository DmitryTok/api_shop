from django.contrib.admin.apps import AdminConfig

class CustomAdminConfig(AdminConfig):
    default_site = 'api_shop.admin.CustomAdminSite'
