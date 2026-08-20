from abc import abstractmethod, ABC
from decimal import Decimal
from typing import Any
from datetime import datetime, date, time
from uuid import UUID


class DjangoFieldConverter(ABC):
    @abstractmethod
    def get_field_type(self, django_field: Any) -> str:
        pass


class CharFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: str) -> str:
        field_type = f"string (max to {django_field.max_length} symbols)"
        return field_type


class IntegerFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: int) -> str:
        return "integer"


class PositiveIntegerFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: int) -> str:
        return "integer (only positive)"


class TextFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: str) -> str:
        return "string"


class FloatFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: float) -> str:
        return "float"


class DateTimeFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: datetime) -> str:
        return "YYYY/mm/dd/hh/mm/ss"


class AutoFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: int) -> str:
        return "integer"


class EmailFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: str) -> str:
        return "string (for example: testemail@test.com)"


class URLFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: str) -> str:
        return "string"


class BigAutoFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: int) -> str:
        return "integer"


class DecimalFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: Decimal) -> str:
        nums_before_decimal = django_field.max_digits - django_field.decimal_places
        return (f"float (up to {nums_before_decimal} digits before "
                f"the decimal point and {django_field.decimal_places} after it)")


class BooleanFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: bool) -> str:
        return "bool (only True/False)"


class DateFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: date) -> str:
        return "YYYY/mm/dd"


class TimeFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: time) -> str:
        return "time (format - hh:mm:ss)"


class JSONFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: dict | list | str | int | None | bool) -> str:
        return "dictionary/list/string/integer/None/bool (only True/False)"


class UUIDFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: UUID) -> str:
        return "string"


class FileFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: str) -> str:
        return "string path to file"


class ImageFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: str) -> str:
        return "string path to image"


class ForeignKeyConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: int) -> str:
        return f"integer ({django_field.related_model._meta.model_name} object id)"


class OneToOneFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: int) -> str:
        return f"integer ({django_field.related_model._meta.model_name} object id)"


class ManyToManyFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: list[int]) -> str:
        return f"integer ({django_field.related_model._meta.model_name} object id)"


class SlugFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: str) -> str:
        return "string"
