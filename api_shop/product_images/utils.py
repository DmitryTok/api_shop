def product_image_upload_path(instance, filename):
    return f"products/{instance.product_variant.sku}/{filename}"
