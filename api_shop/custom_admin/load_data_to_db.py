import json
from typing import TextIO

from django.apps import apps
from django.db import transaction


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
        models = [model_class(**instance["fields"]) for instance in self.list_file]

        with transaction.atomic():
            model_class.objects.bulk_create(models)
