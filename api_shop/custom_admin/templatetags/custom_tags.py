from django import template
from django.apps import apps
import json

from django.contrib import admin

register = template.Library()


MODEL_AND_PYTHON_TYPES_DICT = {
    "CharField": "str",
    "TextField": "str",
    "SlugField": "str",
    "EmailField": "str",
    "URLField": "str",
    "UUIDField": "uuid.UUID",
    "GenericIPAddressField": "str",
    "FilePathField": "str",
    "IntegerField": "int",
    "SmallIntegerField": "int",
    "BigIntegerField": "int",
    "PositiveIntegerField": "int",
    "PositiveSmallIntegerField": "int",
    "PositiveBigIntegerField": "int",
    "FloatField": "float",
    "DecimalField": "decimal.Decimal",
    "BooleanField": "bool",
    "DateField": "datetime.date",
    "DateTimeField": "datetime.datetime",
    "TimeField": "datetime.time",
    "DurationField": "datetime.timedelta",
    "FileField": "str",
    "ImageField": "str",
    "JSONField": "dict",
    "BinaryField": "bytes",
    "ForeignKey": "int",
    "OneToOneField": "int",
    "ManyToManyField": "list[int]",
}


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
    invalid_fields = ("id", "created_at", "updated_at")
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
            fields_dict[field.name] = MODEL_AND_PYTHON_TYPES_DICT.get(field.get_internal_type(), None)
    else:
        for field in model_fields:
            if field.name in invalid_fields:
                continue
            fields_dict[field.name] = MODEL_AND_PYTHON_TYPES_DICT.get(field.get_internal_type(), None)

        for many_to_many_field in many_to_many_fields:
            fields_dict[many_to_many_field.name] = MODEL_AND_PYTHON_TYPES_DICT.get(field.get_internal_type(), None)
    example_json = [
        {
            "model": f"{app_label}.{model_name}",
            "fields": fields_dict
        }
    ]
    example_json = json.dumps(example_json, indent=4, ensure_ascii=False)
    return example_json
