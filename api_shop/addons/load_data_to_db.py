import json

from django.apps import apps
from django.db import transaction


class FixtureLoader:
    def __init__(self, file) -> None:
        self.file = file

    def load_data_to_db(self) -> None:
        if hasattr(self.file, "read"):
            content = self.file.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            list_instances = json.loads(content)
        else:
            list_instances = json.load(self.file)

        if not isinstance(list_instances, list):
            raise ValueError("File content must be list")

        list_models = [instance["model"] for instance in list_instances]
        list_fields = [instance["fields"] for instance in list_instances]

        if not list_models:
            raise ValueError("Every instance must have 'model' key")

        if not list_fields:
            raise ValueError("Every instance must have 'fields' key")

        app_name, model_name = list_instances[0]["model"].split(".")
        model = apps.get_model(app_name, model_name)
        models = [model(**fields) for fields in list_fields]
        with transaction.atomic():
            model.objects.bulk_create(models)
