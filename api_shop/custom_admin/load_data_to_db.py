import datetime
import json
from typing import TextIO

from django.apps import apps
from django.db import transaction, models as db_models


def read_json_file(file: TextIO) -> list[dict]:
    list_file = json.load(file)
    if not list_file:
        raise ValueError("File is empty")
    return list_file


class FixtureLoader:
    def __init__(self, file: TextIO) -> None:
        self.list_file = read_json_file(file)
        self.app_name, self.model_name = self.list_file[0]["model"].split(".")

    def load_data_to_db(self, app_name: str, model_name: str) -> None:
        if not isinstance(self.list_file, list) or not self.list_file:
            raise ValueError("File content must be a non-empty list")

        if self.app_name.strip() != app_name.strip() or self.model_name.strip() != model_name.strip():
            raise ValueError("Model is not correct")

        model_class = apps.get_model(self.app_name, self.model_name)
        models = []
        for instance in self.list_file:
            prepared_fields = {}
            fields = instance["fields"]
            for field, value in fields.items():
                field_to_check = model_class._meta.get_field(field)
                if field_to_check.is_relation and not field_to_check.many_to_many:
                    prepared_fields[f"{field}_id"] = fields[field]
                elif isinstance(field_to_check, db_models.DateTimeField):
                    date_list = [int(part_date) for part_date in value.split("/")]
                    date_time_field = datetime.datetime(*date_list)
                    prepared_fields[field] = date_time_field
                elif isinstance(field_to_check, db_models.DateField):
                    date_list = [int(part_date) for part_date in value.split("/")]
                    date_field = datetime.date(*date_list)
                    prepared_fields[field] = date_field
                else:
                    prepared_fields[field] = value
            model = model_class(**prepared_fields)
            models.append(model)

        with transaction.atomic():
            model_class.objects.bulk_create(models)
