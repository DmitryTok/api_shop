import pytest
from django.core.cache import cache

from users.utils import gen_code


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


def test_gen_code_lock_prevents_duplicate_generation_within_window():
    first_code = gen_code(101, "activation")
    second_code = gen_code(101, "activation")

    assert first_code is not None
    assert second_code is None


def test_gen_code_invalidates_previous_code_on_regeneration():
    old_code = gen_code(102, "activation")
    cache.delete("lock:activation:102")

    new_code = gen_code(102, "activation")

    assert new_code is not None
    assert new_code != old_code
    assert cache.get(f"activation:{old_code}:user_id") is None
    assert cache.get(f"activation:{new_code}:user_id") == 102
    assert cache.get("user:102:activation_code") == new_code


def test_gen_code_password_reset_uses_longer_timeout():
    gen_code(103, "password_reset")

    ttl = cache.ttl("user:103:password_reset_code")
    assert ttl is not None and 890 <= ttl <= 900


def test_gen_code_activation_uses_shorter_timeout():
    gen_code(104, "activation")

    ttl = cache.ttl("user:104:activation_code")
    assert ttl is not None and 290 <= ttl <= 300
