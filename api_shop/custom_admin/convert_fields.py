from abc import abstractmethod, ABC
from decimal import Decimal
from typing import Any
from datetime import datetime, date, time


class DjangoFieldConverter(ABC):
    @abstractmethod
    def get_field_type(self, django_field: Any) -> str:
        pass


class DateTimeFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: datetime) -> str:
        return "date (format: YYYY/mm/dd/hh/mm/ss)"


class DateFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: date) -> str:
        return "date (format: YYY/mm/dd)"


class DecimalFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: Decimal) -> str:
        nums_before_decimal = django_field.max_digits - django_field.decimal_places
        return (f"float (up to {nums_before_decimal} digits before "
                f"the decimal point and {django_field.decimal_places} after it)")


class TimeFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: time) -> str:
        return "time (format: hh:mm:ss)"


class ForeignKeyConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: int) -> str:
        return f"integer ({django_field.related_model._meta.model_name} object id)"


class OneToOneFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: int) -> str:
        return f"integer ({django_field.related_model._meta.model_name} object id)"


class ManyToManyFieldConverter(DjangoFieldConverter):
    def get_field_type(self, django_field: list[int]) -> str:
        return f"integer list (list of {django_field.related_model._meta.model_name} objects id, for ex.: [2, 3, 1])"
