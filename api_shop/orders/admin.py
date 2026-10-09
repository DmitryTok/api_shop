from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product_variant",
        "quantity",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "profile",
        "total_amount",
        "status",
        "payment_status",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_status",
        "payment_method",
    )
    search_fields = (
        "profile__user__email",
        "profile__first_name",
        "profile__last_name",
        "profile__phone",
    )
    readonly_fields = (
        "profile",
        "total_amount",
        "created_at",
    )
    inlines = (OrderItemInline,)
