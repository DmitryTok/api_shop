from whitenoise.storage import CompressedManifestStaticFilesStorage


class TolerantStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """CompressedManifestStaticFilesStorage that doesn't fail collectstatic
    when a third-party CSS/JS file references a static asset that doesn't
    actually exist on disk. jazzmin ships several bundled Bootswatch themes
    whose CSS references .css.map source maps that aren't included in the
    package — a missing source map is harmless (browsers just skip it), but
    the strict manifest storage otherwise aborts the whole build over it.
    """

    def hashed_name(self, name, content=None, filename=None):
        try:
            return super().hashed_name(name, content, filename)
        except ValueError:
            return name
