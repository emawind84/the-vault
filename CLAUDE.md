# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

"The Vault" — a Django web app for managing credentials, backed by HashiCorp Vault. Secret *metadata* (label, username, URL, category, owning groups, timestamps) lives in a regular Django DB; the actual password/config *values* are never persisted there — they're written to and read from Vault per-request. See Architecture below.

## Commands

The Python virtualenv lives at the **repo root** in `env/` (not inside `app/`). Use its interpreter directly rather than activating it:

```bash
# from the app/ directory
../env/Scripts/python.exe manage.py runserver          # dev server, default port 8000
../env/Scripts/python.exe manage.py migrate
../env/Scripts/python.exe manage.py createsuperuser
../env/Scripts/python.exe manage.py test               # run all tests
../env/Scripts/python.exe manage.py test manager.tests.VaultTest   # single test case
../env/Scripts/python.exe manage.py collectstatic --clear
```

Installing/upgrading deps: `../env/Scripts/python.exe -m pip install -r requirements.txt` (run from `app/`).

Local config: create `app/pwd_manager/local_settings.py` (git-ignored, not present by default) with at least `VAULT_HOST` and `VAULT_TOKEN`. See `README.md` for the full Vault init/policy/token walkthrough.

**Test caveat:** `manager.tests.VaultTest` talks to a real Vault instance (`VAULT_HOST`/`VAULT_TOKEN`) — it will fail/hang without one reachable. `users/tests.py` is currently an empty scaffold.

**Harmless startup noise:** every `manage.py` invocation prints `OS error: No module named 'pwd_manager.ldap_settings'` to stdout. `pwd_manager/settings.py` does `from .local_settings import *` then `from .ldap_settings import *` inside one `try/except ImportError` that just prints and continues — `ldap_settings.py` isn't expected to exist unless you've added it.

### Docker

`./docker-auto.sh [--dev|--prod] <command>` wraps `docker-compose` (auto-installs a pinned `docker-compose` version) and adds Vault helpers: `up`, `down`, `ps`, `logs`, `vault-init`, `vault-unseal`, `vault-login`, `vault-renew`, `vault-cmd <args>`, `stop-all`. Default (no `--dev`) uses `common-service.yml` + `docker-compose.yml` (nginx + Vault backed by Consul); `--dev` uses `docker-compose-dev.yml` (single Vault dev-mode container, root token `myroot`).

Inside the container, `app/pwd-manager-auto.sh` is the entrypoint: it activates the image's own venv, runs `migrate`, then either runs `collectstatic` + `runserver 0.0.0.0:8091` (no args passed to the container) or `exec`s whatever `manage.py <args>` was passed instead.

## Architecture

**Django project** `pwd_manager` (Python 3.6, Django 2.2.24) with two first-party apps:

- **`manager`** — the core app: `Secret`/`Vault` models, secret CRUD views, Vault integration.
- **`users`** — thin wrappers around Django's built-in auth views (login/logout/register/password change/reset), plus custom user-edit views. Templates for both apps share the same base layout at `manager/templates/manager/base.html`.
- **`auth`** (not a registered Django app, just a module) — custom authentication backends, selected via `AUTHENTICATION_BACKENDS` in `local_settings.py`: `settings_backend.SettingsBackend` (checks `ADMIN_LOGIN`/`ADMIN_PASSWORD` from settings), `ldap_backend.py` (`django_auth_ldap` wrapper, two configurable instances `LDAPBackend1`/`LDAPBackend2`), `pmis_backend.py` (calls an external PMIS login endpoint). `social_django` (Google/GitHub/Kakao OAuth) is also wired in as an installed app/URL include.

**Secret storage split:** `manager.Secret` (DB) never stores real password/config values — `manager/views.py`'s `new_secret`/`edit_secret` always blank `password`/`config` before `.save()`. The real values are written to/read from HashiCorp Vault via `manager/vault.py`'s `VaultClient` (thin `hvac` wrapper, KV v1), at path `{vault.path}/{secret.label}`. Every user gets their own private Vault mount path (`manager.Vault.path`, a random string), lazily created by `VaultClient.get_vault_or_create(user)` on first use.

**Access control:** `manager/decorators.py`'s `@groups_required` restricts a secret view to users sharing at least one of the secret's assigned Django `Group`s (via the `Secret.groups` M2M) — secrets with no groups assigned are unrestricted by this check. Ownership is enforced separately, ad hoc in each view (`secret.creator != request.user` → `Http404`), not via the decorator.

**Config layering & auth gotcha:** real per-environment secrets (Vault host/token, `AUTHENTICATION_BACKENDS`, OAuth keys, `ADMIN_LOGIN`/`ADMIN_PASSWORD`) live only in `app/pwd_manager/local_settings.py` (git-ignored). Because that file typically overrides `AUTHENTICATION_BACKENDS` entirely, a plain Django superuser created via `createsuperuser` (which relies on `ModelBackend`) generally **cannot log in** unless `local_settings.py` re-adds `ModelBackend` — auth instead goes through whichever custom/LDAP/social backend is configured there.

**Frontend:** server-rendered Django templates only, no JS framework or build step. Design system lives in `app/local-static/css/app.css` + `app/local-static/js/app.js` (source dir per `STATICFILES_DIRS`; collected into `app/static/` via `collectstatic`). Forms render generically through `manager/templates/manager/includes/form.html`, which loops over any Django form's fields — there's no per-field/per-form template. Icons are inline SVG via a template tag (`{% load icons %}` / `{% icon 'name' %}`, defined in `manager/templatetags/icons.py`), not an icon font or CDN. Dark/light theme is CSS-variable-driven with a `localStorage`-persisted toggle.

**Session behavior:** `django_session_timeout` middleware logs users out after 10 minutes of inactivity (`SESSION_EXPIRE_SECONDS = 600` in `settings.py`) — worth remembering when manually testing long flows.
