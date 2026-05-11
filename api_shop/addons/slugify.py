from django.utils.text import slugify


def generate_unique_slug(model, value: str) -> str:
    base_slug = slugify(value)
    slug = base_slug
    counter = 1

    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug