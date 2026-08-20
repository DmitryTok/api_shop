from django import template
from django.apps import apps
import json

from django.contrib import admin

from custom_admin import convert_fields


register = template.Library()


@register.simple_tag
def generate_example_json(app_label: str, model_name: str) -> str:
    model_class = apps.get_model(app_label, model_name)
    model_admin = admin.site._registry.get(model_class)

    if model_admin and model_admin.fields:
        admin_fields = list(model_admin.fields)
    else:
        admin_fields = None
    model_fields = model_class._meta.concrete_fields
    many_to_many_fields = model_class._meta.many_to_many
    invalid_fields = ("id", "created_at", "updated_at", "groups", "user_permissions")
    fields_dict = {}
    if admin_fields:
        for field_name in admin_fields:
            if isinstance(field_name, (list, tuple)):
                continue
            try:
                field = model_class._meta.get_field(field_name)
            except Exception as e:
                return f"Error: {e}, during creating admin fields for model"
            if field.name in invalid_fields:
                continue
            class_converter = getattr(convert_fields, f"{field.get_internal_type()}Converter")
            simple_field = class_converter()
            fields_dict[field.name] = simple_field.get_field_type(django_field=field)
    else:
        for field in model_fields:
            if field.name in invalid_fields:
                continue
            class_converter = getattr(convert_fields, f"{field.get_internal_type()}Converter")
            simple_field = class_converter()
            fields_dict[field.name] = simple_field.get_field_type(django_field=field)

        for many_to_many_field in many_to_many_fields:
            if many_to_many_field.name in invalid_fields:
                continue
            class_converter = getattr(convert_fields, f"{many_to_many_field.get_internal_type()}Converter")
            simple_field = class_converter()
            fields_dict[many_to_many_field.name] = simple_field.get_field_type(django_field=many_to_many_field)
    example_json = [
        {
            "model": f"{app_label}.{model_name}",
            "fields": fields_dict
        }
    ]
    example_json = json.dumps(example_json, indent=4, ensure_ascii=False)
    return example_json
