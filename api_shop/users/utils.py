from django.core.cache import cache
from django.utils.crypto import get_random_string


def gen_code(user_id: int, task_type: str):
    lock_key = f"lock:{task_type}:{user_id}"

    if not cache.add(lock_key, "locked", timeout=30):
        return None

    code_timeout = 900 if task_type == "password_reset" else 300

    user_old_code_key = f"user:{user_id}:{task_type}_code"
    old_code = cache.get(user_old_code_key)

    if old_code:
        cache.delete(f"{task_type}:{old_code}:user_id")
        cache.delete(user_old_code_key)

    new_code = get_random_string(length=6, allowed_chars='0123456789')

    cache.set(f"{task_type}:{new_code}:user_id", user_id, timeout=code_timeout)
    cache.set(user_old_code_key, new_code, timeout=code_timeout)

    return new_code
