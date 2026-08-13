from django.contrib import admin


class CustomModelAdmin(admin.ModelAdmin):
    change_list_template = "admin/custom_change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        is_custom = request.GET.get('custom') == '1'
        extra_context['custom'] = is_custom

        if is_custom:
            q = request.GET.copy()
            q.pop('custom')
            request.GET = q
            request.META['QUERY_STRING'] = q.urlencode()

        return super().changelist_view(request, extra_context=extra_context)
