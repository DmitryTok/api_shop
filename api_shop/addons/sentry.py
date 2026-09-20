import sentry_sdk


def init_sentry(dsn, environment, send_default_pii=False):
    if environment == "local":
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        send_default_pii=send_default_pii,
    )
