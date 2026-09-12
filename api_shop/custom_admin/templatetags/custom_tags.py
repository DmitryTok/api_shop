from django import template
from django.apps import apps
import json
import inspect

from custom_admin import convert_fields

register = template.Library()


def get_manager_hint(field):
    field_classes = inspect.getmro(type(field))

    for field_class in field_classes:
        converter_name = f"{field_class.__name__}Converter"
        converter_class = getattr(convert_fields, converter_name, None)

        if converter_class:
            return converter_class().get_field_type(django_field=field)

    return field.description % field.__dict__


@register.simple_tag
def generate_example_json(app_label: str, model_name: str) -> str:
    model_class = apps.get_model(app_label, model_name)
    model_fields = [
        field for field in model_class._meta.get_fields() if not field.auto_created
    ]
    invalid_fields = ("id", "created_at", "updated_at", "groups", "user_permissions")

    fields_dict = {}

    for field in model_fields:
        if field.name in invalid_fields:
            continue
        fields_dict[field.name] = get_manager_hint(field)

    example_json = [
        {
            "model": f"{app_label}.{model_name}",
            "fields": fields_dict,
        }
    ]

    return json.dumps(example_json, indent=4, ensure_ascii=False)
