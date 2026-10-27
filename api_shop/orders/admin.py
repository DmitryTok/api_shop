from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = (
        "product_name",
        "sku",
        "size",
        "color",
        "unit_price",
        "quantity",
        "line_total",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Read-only: orders are created through the API (checkout) only."""

    list_display = (
        "id",
        "user",
        "status",
        "currency_code",
        "total_amount",
        "created_at",
    )
    list_filter = (
        "status",
        "currency_code",
    )
    search_fields = (
        "email",
        "phone",
        "last_name",
    )
    list_select_related = ("user",)
    inlines = (OrderItemInline,)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
