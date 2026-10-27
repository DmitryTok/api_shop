import pytest
from django.core.exceptions import ImproperlyConfigured

from addons.env import getenv_bool, getenv_int, getenv_list


def test_getenv_bool_returns_default_when_unset(monkeypatch):
    monkeypatch.delenv("SOME_BOOL", raising=False)

    assert getenv_bool("SOME_BOOL", default=True) is True
    assert getenv_bool("SOME_BOOL", default=False) is False


@pytest.mark.parametrize("raw_value", ["1", "true", "True", "yes", "on"])
def test_getenv_bool_parses_truthy_values(monkeypatch, raw_value):
    monkeypatch.setenv("SOME_BOOL", raw_value)

    assert getenv_bool("SOME_BOOL") is True


@pytest.mark.parametrize("raw_value", ["0", "false", "False", "no", "off"])
def test_getenv_bool_parses_falsy_values(monkeypatch, raw_value):
    monkeypatch.setenv("SOME_BOOL", raw_value)

    assert getenv_bool("SOME_BOOL") is False


def test_getenv_bool_rejects_invalid_value(monkeypatch):
    monkeypatch.setenv("SOME_BOOL", "maybe")

    with pytest.raises(ImproperlyConfigured):
        getenv_bool("SOME_BOOL")


def test_getenv_int_returns_default_when_unset(monkeypatch):
    monkeypatch.delenv("SOME_INT", raising=False)

    assert getenv_int("SOME_INT", default=42) == 42


def test_getenv_int_parses_valid_value(monkeypatch):
    monkeypatch.setenv("SOME_INT", "10")

    assert getenv_int("SOME_INT") == 10


def test_getenv_int_rejects_non_numeric_value(monkeypatch):
    monkeypatch.setenv("SOME_INT", "not-a-number")

    with pytest.raises(ImproperlyConfigured):
        getenv_int("SOME_INT")


def test_getenv_int_raises_when_unset_and_no_default(monkeypatch):
    monkeypatch.delenv("SOME_INT", raising=False)

    with pytest.raises(ImproperlyConfigured):
        getenv_int("SOME_INT")


def test_getenv_list_returns_empty_list_when_unset(monkeypatch):
    monkeypatch.delenv("SOME_LIST", raising=False)

    assert getenv_list("SOME_LIST") == []


def test_getenv_list_splits_and_strips_values(monkeypatch):
    monkeypatch.setenv("SOME_LIST", "a, b ,c")

    assert getenv_list("SOME_LIST") == ["a", "b", "c"]
