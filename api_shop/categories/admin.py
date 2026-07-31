from django.contrib import admin

from .models import Category, Subcategory


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1
    fields = (
        "name",
        "slug",
        "is_active",
        "is_hidden",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "is_active",
        "is_hidden",
        "created_at",
    )
    search_fields = (
        "name",
        "slug",
    )
    list_filter = (
        "is_active",
        "is_hidden",
    )
    inlines = (SubcategoryInline,)


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "category",
    )
    search_fields = (
        "name",
        "slug",
    )