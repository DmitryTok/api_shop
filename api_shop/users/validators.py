import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class RegexPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _(
                    "This password is too short. It must contain at least 8 characters."
                ),
                code='password_too_short',
            )

        if len(password) > 128:
            raise ValidationError(
                _(
                    "This password is too long. It must not exceed 128 characters."
                ),
                code='password_too_long',
            )

        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _(
                    "This password must contain at least one uppercase letter (A-Z)."
                ),
                code='password_no_upper',
            )

        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _(
                    "This password must contain at least one lowercase letter (a-z)."
                ),
                code='password_no_lower',
            )

        if not re.search(r'\d', password):
            raise ValidationError(
                _("This password must contain at least one digit."),
                code='password_no_digit',
            )

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _(
                    "This password must contain at least one special character (!@#$%^&*...)."
                ),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            "Your password must be at least 8 characters long, contain upper and lower case letters, "
            "one digit and one special character."
        )
