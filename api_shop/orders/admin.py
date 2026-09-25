from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product_variant",
        "quantity",
        "price",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "total_amount",
        "status",
        "payment_status",
        "delivery_method",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_status",
        "delivery_method",
        "payment_method",
    )
    search_fields = (
        "user__email",
        "first_name",
        "last_name",
        "phone",
    )
    readonly_fields = (
        "user",
        "total_amount",
        "created_at",
    )
    inlines = (OrderItemInline,)