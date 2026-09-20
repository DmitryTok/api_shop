# Infrastructure runbook

Operational reference for WearlyShop's backend: what's running where, how a deploy happens, and what to check when something breaks. This doc only covers infra/ops — for domain/model architecture and dev commands, see [`README.md`](../README.md).

## Topology

| Environment | Trigger              | Render services                    |
| ----------- | --------------------- | ----------------------------------- |
| local       | `docker compose up`   | `db`, `redis`, `web`, `nginx` (all in `docker-compose.yml`) |
| staging     | push to `dev`         | `web` (Docker service) + `api_shop_celery` (Background Worker) |
| production  | push to `main`        | `web` (Docker service) + `api_shop_celery` (Background Worker) |

Staging and production each run **one container** built from the repo's `Dockerfile`, containing nginx + Gunicorn as sibling processes under `supervisord`:

```
Render edge (TLS termination)
        │  sets X-Forwarded-Proto
        ▼
   nginx (binds $PORT, from entrypoint.sh + prod.conf.template)
        │  proxy_pass, rate-limited (see nginx/prod.conf.template)
        ▼
   Gunicorn (fixed 127.0.0.1:8001, --chdir /app/api_shop)
        │
        ▼
   Django  ──►  Postgres (DATABASE_URL, e.g. Neon, ssl_require=True)
        └──►  Redis (REDIS_URL — cache/throttling/activation codes)
```

The Celery worker (`api_shop_celery`) is a **separate Render service**, not defined anywhere in this repo (no worker in `docker-compose.yml`, the `Dockerfile`, or any deploy config). Its command is configured directly in the Render dashboard — `git log`/`git blame` will never show it. Losing track of this is the single most common cause of "emails never arrive" — see [Incident: emails not sending](#incident-emails-not-sending).

Two separate Redis databases, same `REDIS_URL` host:
- db 0 — `CELERY_BROKER_URL`, the task queue
- db 1 — `REDIS_URL`, Django's cache (also backs `AnonRateThrottle` and the activation/password-reset code locks)

## Deploys

Driven by GitHub Actions (`.github/workflows/ci.yml`), not Render's own git auto-deploy (kept off on purpose so it can't race the webhook):

1. `lint` job — `uv run pre-commit run --all-files` (with `SKIP=no-commit-to-branch`, since that hook only makes sense for a local `git commit`).
2. `test` job — spins up ephemeral Postgres + Redis service containers, runs `uv run pytest`.
3. `deploy-staging` (on push to `dev`) / `deploy-production` (on push to `main`), each only after `lint` and `test` pass:
   - `POST` the environment's Render deploy hook (`RENDER_DEPLOY_HOOK_STAGING_URL` / `RENDER_DEPLOY_HOOK_PRODUCTION_URL`, GitHub Actions secrets).
   - Poll `<env>/health/` every 15s for up to 5 minutes.
   - Run `scripts/smoke_test.sh <env-url>` — plain `GET`-only checks (health, Swagger UI, a static file, the public products list). Safe to run against production; does not create or modify data.

The base URLs (`STAGING_BASE_URL`, `PRODUCTION_BASE_URL`) are GitHub Actions repo/environment **variables**, not secrets — check the repo's Settings → Environments if you need the actual hostnames.

### Rolling back

Render keeps prior deploys per service. From the Render dashboard: open the affected service (`web` or `api_shop_celery`) → **Deploys** tab → pick a previous successful deploy → **Redeploy**. This bypasses GitHub Actions entirely, so do it only when a bad deploy is already live and you need to stop the bleeding — follow up with a proper revert commit through the normal `dev`/`main` flow afterward so Render's history and the git history don't diverge silently.

### What's on Render but not in this repo

These only exist in the Render dashboard — grep/`git blame` will never find them:
- The `api_shop_celery` Background Worker service and its exact Docker Command (see [Celery](#celery-worker) below).
- All environment variables for both `web` and `api_shop_celery` (staging and production each have their own set).
- Render → Account/Service Settings → Notifications ("Deploy failed" / "Service unhealthy" alerts) — separate from Sentry, see [Alerting](#alerting).

A `render.yaml` (Render's IaC format) now exists at the repo root, covering staging + production `web` and Celery-worker services. It has **not been synced to Render yet** — service names, plan, and region in it are best-effort guesses from git history (an earlier, staging-only `render.yaml` existed and was deliberately deleted in favor of dashboard-managed config) and need to be confirmed against the live dashboard first. See [Setting up the Render Blueprint](#setting-up-the-render-blueprint) below.

## Setting up the Render Blueprint

`render.yaml` is Render's Infrastructure-as-Code format ("Blueprint"): it describes each service's shape (plan, region, branch, Docker command, which env vars exist) as one file in git, instead of that config living only in dashboard clicks. Render reconciles this declaratively — it does **not** replay a sequence of steps, it just diffs the file against live state and applies the difference.

How the sync actually behaves, since it's easy to get wrong:
- Render matches a blueprint's services to existing ones **by the `name:` field**, nothing else. A name that doesn't exactly match an existing service creates a brand-new duplicate service instead of adopting the real one.
- Env vars with a literal `value:` in the file are **overwritten on every sync** — if you hand-edit one of those in the dashboard, the next sync silently reverts it. Only put non-secret, environment-wide constants there (see `wearlyshop-shared` in the file).
- Env vars marked `sync: false` are the opposite: Render creates an *empty slot* for them on first sync and then **never touches their value again** — you fill them in by hand in the dashboard, once, and subsequent syncs leave them alone. This is how secrets stay out of git.
- `autoDeployTrigger: "off"` on every service here means the Blueprint only manages *configuration* — the actual deploy (new image) still goes through the GitHub Actions `deploy-staging`/`deploy-production` jobs (see [Deploys](#deploys) above), not Render's own git integration.

### First-time setup

1. **Before syncing anything**, open each live service in the Render dashboard and copy its exact `name`, `plan`, and `region` into the corresponding block in `render.yaml` — every value currently marked `# TODO: confirm` is a placeholder guessed from old git history, not verified against what's actually running. Getting a name wrong creates a duplicate service (see above), so this step isn't optional.
2. Render Dashboard → **New → Blueprint** → select this repository.
3. Render parses `render.yaml` and shows a preview of what it will create/update. Check that every service it plans to touch is one you recognize — if it says "create" for something you expected it to "update", stop and fix the `name:` field first.
4. Confirm the sync.
5. For each of the 4 services, go to its **Environment** tab and fill in every variable marked `sync: false` in the file. Where those values come from:

   | Variable | Source |
   | --- | --- |
   | `SECRET` | Generate one per environment: `python -c "import secrets; print(secrets.token_urlsafe(64))"`. Staging and production must each get their own. |
   | `ALLOWED_HOSTS` | The hostname Render assigns the service (visible on the service's own Settings page once it exists, e.g. `wearlyshop-staging-web.onrender.com`) plus any custom domain. Comma-separated, no scheme, no trailing slash. |
   | `DATABASE_URL` | Neon console → the relevant project → Connection string (use the pooled connection — `settings.py` parses this with `ssl_require=True`). |
   | `REDIS_URL` | Upstash console → the Redis database → connection string, with `/1` appended (db 1 = Django cache/throttling). |
   | `CELERY_BROKER_URL` | Same Upstash database, connection string with `/0` appended (db 0 = Celery queue). |
   | `SENTRY_DSN` | sentry.io → org `wearly-6u` → project `wearly-shop-backend` → Settings → Client Keys (DSN). Needed on both the web and Celery service in each environment. |
   | `RESEND_API_KEY` | resend.com dashboard → API Keys. |
   | `DEFAULT_FROM_EMAIL` | An address on a domain that's actually verified in Resend (Resend → Domains — DKIM/SPF already configured there). |
   | `GOOGLE_CLIENT_ID` | Google Cloud Console → APIs & Services → Credentials → the relevant OAuth 2.0 Client ID. |
   | `CLOUDINARY_CLOUD_NAME` / `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET` | Cloudinary Dashboard → Account Details. |
   | `CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS` | The frontend's real deployed URL (Vercel project — check the current domain there; don't assume an old one is still correct). |
   | `SUPER_LOGIN` / `SUPER_PASSWORD` | Your own choice — credentials for the superuser `make superuser` / `create_default_superuser` bootstraps. |

   The Celery worker services only need a subset of these (`SECRET`, `ALLOWED_HOSTS`, `DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL`, `SENTRY_DSN`, `RESEND_API_KEY`, `DEFAULT_FROM_EMAIL`) — `settings.py` is imported by the worker too so it still needs the vars it validates at import time, but Cloudinary/CORS/CSRF/Google/superuser vars are only ever read by HTTP request handling, which the worker never does.

### Making changes later

Edit `render.yaml`, get it reviewed/merged like any other code change, then re-run the sync from the Blueprint's page in the Render dashboard (or push, if the Blueprint is set to auto-sync on push — that's a separate setting from `autoDeployTrigger`, which only governs deploys, not config sync). Only fields with a literal `value:` or structural fields (plan/region/branch/dockerCommand/etc.) change anything on sync — `sync: false` vars already filled in are left alone.

## Health checks

`GET /health/` (`api_shop/addons/health.py`):

```json
{
  "status": "ok",
  "database": "ok",
  "redis": "ok",
  "environment": "production",
  "version": "<RENDER_GIT_COMMIT>"
}
```

- **Database is a hard dependency** — unreachable DB returns HTTP 503, which Render treats as unhealthy and restarts the container.
- **Redis is a soft dependency** — reported in the body, never fails the check by itself. But in practice a broken Redis still breaks the whole API: `CACHES` has `IGNORE_EXCEPTIONS: False`, and DRF's global `AnonRateThrottle` hits the cache on every request. So "Redis unreachable" in this payload is not actually low-severity — treat it as urgent.
- `version` comes from Render's `RENDER_GIT_COMMIT` env var (automatically set by Render, not something to configure).

Also used by the Docker `HEALTHCHECK` (`Dockerfile`) and by CI's post-deploy polling.

## Incident: emails not sending

Two independent, both-silent failure points. Check both:

1. **Is the Celery worker actually running?** Nothing consumes `CELERY_BROKER_URL` (Redis db 0) unless `api_shop_celery` is up on Render — `.delay()` just enqueues and returns 200 either way, so the API gives no indication anything is wrong.
   - Render dashboard → `api_shop_celery` service → confirm it's running, check its logs.
   - Confirm its Docker Command matches exactly:
     ```
     celery --workdir=api_shop -A api_shop worker -l info --without-heartbeat --without-gossip --without-mingle --pool=solo
     ```
     - Missing `--workdir=api_shop` → `Module 'api_shop' has no attribute 'celery'` (the Celery app is one directory deeper than the container's `/app`).
     - Missing `--pool=solo` → Celery defaults `concurrency` to the host's visible CPU count (16 on Render's underlying shared host, regardless of the plan's actual memory), forks that many workers, OOMs, and the service restart-loops.
   - Locally, nothing runs a worker automatically either — start one manually from `api_shop/`: `uv run celery -A api_shop worker -l info`.

2. **Did the send fail after retries were exhausted?** `users/services/email.py:send_email_code()` still catches every exception to clean up the Redis lock key, but now re-raises instead of swallowing it. `users/tasks.py:send_email_code_task` retries on any exception (`autoretry_for=(Exception,)`, up to 3 times with exponential backoff + jitter, capped at 10 minutes) except `User.DoesNotExist`, which is permanent and not retried. Once all retries are exhausted the task ends in `FAILURE` and Sentry (via `CeleryIntegration`, wired in `addons/sentry.py`) reports it as an Issue — check Sentry first for a bad `RESEND_API_KEY` or a Resend outage. Sentry only reports the *final* failure, not each individual retry attempt.

3. **Is a stale lock suppressing the send entirely?** `users/utils.py:gen_code()` sets `lock:{task_type}:{user_id}` in Redis for 30s via `cache.add()`. If that key is already set, `gen_code()` returns `None` and *no email is even attempted* — no error surfaced to the caller. This is the usual explanation for "I clicked resend and nothing happened" within the same 30 seconds.

## Celery worker

See [Topology](#topology) and [Incident: emails not sending](#incident-emails-not-sending) above for the failure modes. Operationally:

- `django-celery-beat` is installed but **no periodic tasks are defined** — the worker only ever processes on-demand tasks from `.delay()` calls.
- `CELERY_BROKER_TRANSPORT_OPTIONS = {"polling_interval": 15}` in `settings.py` caps idle `BRPOP` frequency against the broker. Combined with `--without-heartbeat --without-gossip --without-mingle` on the worker command (irrelevant for a single lone worker, only matter for multi-worker coordination/Flower), this keeps an idle worker's command volume low — without both, one idle worker runs several million Redis commands/month, which matters on a metered plan (Upstash).
- `users/tasks.py:send_email_code_task` retries with exponential backoff + jitter (`retry_backoff=True`, capped at `retry_backoff_max=600` seconds, `max_retries=3`) on any exception except `User.DoesNotExist`, which is treated as permanent and never retried. Confirmed locally via `Task.apply()` with no `RESEND_API_KEY` set: three retries (`Retry in 0s / 0s / 1s`), then `FAILURE`, with the Redis lock key (`lock:{task_type}:{user_id}`) cleaned up on every attempt including the final one.

## Alerting

Two independent layers — neither substitutes for the other:

- **Sentry** (application errors): org `wearly-6u`, project `wearly-shop-backend`, free Developer plan. Alert rule: "High priority issues" → Email, set at project creation. `SENTRY_DSN` must be set on **both** the `web` and `api_shop_celery` Render services to catch errors from each. Sentry only sees exceptions that reach application code — it can't see a deploy that never starts or a container that fails its health check.
  - As of the last DevOps roadmap pass, `sentry_sdk.init()` lives in `addons/sentry.py` (`init_sentry(dsn, environment)`), called from `settings.py`. It's a no-op whenever `APP_ENV=local`, regardless of whether `SENTRY_DSN` is set — so local development never reports to Sentry even with a real DSN in `.env`.
  - The temporary `/sentry-debug/` endpoint used to end-to-end verify this (an unauthenticated route that always threw `ZeroDivisionError`) has been removed from `urls.py` now that staging verification is done.
  - `init_sentry()` explicitly passes `integrations=[CeleryIntegration(monitor_beat_tasks=False)]` rather than relying on Sentry SDK's auto-detection of the installed `celery` package. Because `celery.py` imports Django settings (which calls `init_sentry()`) at worker boot, this runs in the `api_shop_celery` process too, not just `web`. `monitor_beat_tasks=False` is deliberate — `django-celery-beat` is installed but no periodic tasks exist, so there's nothing for Sentry's Crons feature to monitor yet. Practical effect: Sentry only creates an Issue once a task's retries are fully exhausted (a `celery.exceptions.Retry` during an in-progress retry is not itself reported), so a task that eventually succeeds after 2 retries never shows up in Sentry at all.
- **Render notifications** (deploy/infra failures Sentry can't see): Render → Account/Service Settings → Notifications, enable "Deploy failed" and "Service unhealthy" for both services.

## Security surface (nginx)

`nginx/prod.conf.template` (staging/production) and `nginx/dev.conf` (local) both define three rate-limit zones — `general` (10r/s), `admin_login` (5r/m), `api` (20r/s) — and drop common scanner paths (`wp-admin`, `.env`, `phpmyadmin`, `xmlrpc.php`, `.git`) before they reach Django. One behavioral difference between the two: prod returns `403` for those scanner paths, dev returns `444` (connection dropped, no response) — if you're diffing nginx behavior between environments, that's expected, not a bug.

`X-Forwarded-Proto` handling differs deliberately: prod forwards `$http_x_forwarded_proto` (Render's edge already terminates TLS and sets this before the request reaches the container — substituting nginx's own scheme would make every request look like plain HTTP and break `SECURE_SSL_REDIRECT`/secure cookies), while dev forwards `$scheme` directly (nginx itself is the only TLS-terminating hop, and there is none locally).

## Useful commands

```bash
# Local: tail logs for one service
docker compose logs -f web

# Local: open a Django shell inside the running container
docker compose exec web python api_shop/manage.py shell

# Local: run a one-off management command
docker compose exec web python api_shop/manage.py <command>

# Smoke-test any deployed environment by hand
./scripts/smoke_test.sh https://<env-host>

# Inspect a Redis key set by users/utils.py:gen_code() (note the :1: version
# prefix Django's cache backend adds by default — empty prefix, version 1)
redis-cli -u "$REDIS_URL" GET ":1:user:<id>:activation_code"
```
