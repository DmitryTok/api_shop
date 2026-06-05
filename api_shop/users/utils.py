from django.core.cache import cache
from django.utils.crypto import get_random_string


def gen_activation_user_code(user_id: int):
    code = get_random_string(length=6, allowed_chars='0123456789')
    code_key = f"activation:{code}:user_id"

    cache.set(code_key, user_id, timeout=300)

    return code
