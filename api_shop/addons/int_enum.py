class BaseIntEnumMixin:
    @classmethod
    def choices(cls):
        return [(member.value, member.name) for member in cls]
