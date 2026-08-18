# THE VAULT

A Django web application for managing credentials, backed by [HashiCorp Vault](https://www.vaultproject.io/) for secure secret storage.

## Architecture

The stack is made up of four services (see [docker-compose.yml](docker-compose.yml)):

| Service   | What it is                                                         |
|-----------|---------------------------------------------------------------------|
| `manager` | The Django application (this repo's [app](app) folder)              |
| `vault`   | HashiCorp Vault, where the actual credentials are stored             |
| `consul`  | Vault's storage backend                                             |
| `nginx`   | Reverse proxy in front of `manager`, also serves static files        |

`manager` talks to `vault` over HTTP using a Vault token (`VAULT_TOKEN`). Vault itself persists its data in `consul`, not in the `manager` database — the Django database only holds application data (users, groups, sessions, etc.), never secrets.

## Prerequisites

- Python 3 and `pip`
- Docker and `docker-compose` (for the containerized dev/prod workflow — `docker-auto.sh` will install a pinned `docker-compose` version automatically if it's missing)

## Local development (without Docker)

This runs the Django app directly on your machine, pointing at a Vault instance of your choice (e.g. one started with `docker-auto.sh --dev up`, see below).

Upgrade pip to the latest version:

    python -m pip install --upgrade pip

Install `virtualenv`:

    pip install --user virtualenv

From the [app](app) folder, create a virtual environment using Python 3, so the project's dependencies don't collide with other Python projects on your machine:

    cd app
    virtualenv env --python=python3

If everything went well you'll see a new `env` folder inside `app`.

Activate the environment:

    source env/bin/activate

Your prompt should now be prefixed with `(env)`.

Install the required modules:

    pip install -r requirements.txt

Initialize the database:

    python manage.py migrate

Create a superuser for managing users and groups:

    python manage.py createsuperuser

Before starting the application, some configuration is required. Create a new file named `local_settings.py` inside `app/pwd_manager` (next to `settings.py`) with any settings you need to override — see [Configuration](#configuration) below.

At minimum you need to point the app at a Vault instance:

    VAULT_HOST
    VAULT_TOKEN

If you don't have a Vault token yet, see [Initializing Vault for the first time](#initializing-vault-for-the-first-time).

Now you're ready to run the application:

    ./pwd-manager-auto.sh

## Local development with Docker

Instead of running Python locally, you can bring up the whole stack (app + a dev-mode Vault) with Docker:

    ./docker-auto.sh --dev up

This uses [docker-compose-dev.yml](docker-compose-dev.yml), which:

- builds the `manager` image from [app](app) instead of pulling it from a registry,
- starts Vault in **dev mode** (`VAULT_DEV_ROOT_TOKEN_ID=myroot`) — dev mode auto-unseals and keeps everything in memory, so there's no init/unseal step to worry about locally,
- exposes the app on `$MANAGER_LISTEN_PORT` (see [.env](.env)).

For this workflow, `local_settings.py` goes in the **repository root** (next to `docker-compose-dev.yml`), not under `app/pwd_manager` — it gets volume-mounted into the container at `pwd_manager/local_settings.py`. `VAULT_TOKEN=myroot` and `VAULT_HOST=http://vault:8200` are already wired up in `docker-compose-dev.yml`, so you don't need to set them yourself.

Useful commands (see [docker-auto.sh command reference](#docker-autosh-command-reference) for the full list):

    ./docker-auto.sh --dev logs manager   # follow the app logs
    ./docker-auto.sh --dev down           # stop and remove the containers

## Configuration

The app reads its configuration from [app/pwd_manager/settings.py](app/pwd_manager/settings.py), which at the end imports `local_settings.py` (and `ldap_settings.py`) if present. `local_settings.py` is git-ignored — it's where machine- or environment-specific values and secrets belong. Location depends on how you're running the app: see the previous two sections.

Commonly overridden settings:

| Setting          | Purpose                                                                 |
|------------------|--------------------------------------------------------------------------|
| `SECRET_KEY`     | Django's cryptographic signing key — must be unique per environment      |
| `DEBUG`          | Must be `False` in production                                            |
| `ALLOWED_HOSTS`  | Also settable as the `ALLOWED_HOSTS` env var (comma-separated)            |
| `VAULT_HOST`     | URL of the Vault server, e.g. `http://vault:8200`                        |
| `VAULT_TOKEN`    | Vault token used by the app — see [Vault tokens](#vault-tokens-policy--renewal) |
| `EMAIL_*`        | SMTP settings, if the app needs to send email                            |
| `AUTHENTICATION_BACKENDS` | LDAP / other auth backends, e.g. `auth.ldap_backend.LDAPBackend1` |

## Production deployment

### CI/CD

Jenkins builds the `manager` Docker image (from [app/Dockerfile](app/Dockerfile)) and pushes it to our Docker Hub registry (`$REGISTRY_URL` — currently `sangah`, see [.env](.env)). We may move this to a private registry on AWS (e.g. ECR) in the future; the workflow below doesn't change either way, only `REGISTRY_URL` and how you authenticate to it would.

### Deploying / updating the stack

On the production host:

1. Edit [.env](.env) as needed — image tag (`MANAGER_VERION`), registry (`REGISTRY_URL`), listen port (`MANAGER_LISTEN_PORT`), allowed hosts (`ALLOWED_HOSTS`), and data directories (`VAULT_DATA_HOME`, `MANAGER_DATA_HOME`).
2. Create `local_settings.py` in the repository root with the production overrides (new `SECRET_KEY`, `DEBUG = False`, email/LDAP settings, etc. — see [Configuration](#configuration)). Generate a fresh secret key with:

       python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

3. Log in to the registry, then pull and start everything:

       ./docker-auto.sh login
       ./docker-auto.sh up

   `up` pulls the latest images, rebuilds `nginx`, and starts the stack with `docker-compose up -d --remove-orphans`.

Since `DEBUG=False` disables Django's static file serving, static files are collected into a shared volume and served by `nginx` instead — this happens automatically as part of the `manager` container's entrypoint ([app/pwd-manager-auto.sh](app/pwd-manager-auto.sh)); no manual `collectstatic` step is needed with this Docker setup.

> **Security note:** the production compose file publishes Vault's port (`8200`) directly on the host, and Vault's own UI is enabled (`ui = true` in [vault-config/config.hcl](vault-config/config.hcl)). Make sure that port is only reachable from trusted networks (firewall / security group), since it's the same endpoint used for unsealing and administration.

### Initializing Vault for the first time

The very first time Vault starts against empty storage, it is **uninitialized and sealed** — it holds no data and can't serve requests until it's initialized and unsealed.

1. Initialize it:

       ./docker-auto.sh vault-init

   This runs `vault operator init` and prints **5 unseal key shares and one initial root token**. Record all of them somewhere safe (e.g. a password manager) — they are shown only once and Vault does not store them. Do not commit them anywhere.

2. Unseal it. By default Vault uses a 3-of-5 Shamir threshold, so you need **any 3 of the 5 unseal keys**, entered one at a time:

       ./docker-auto.sh vault-unseal   # run 3 times, pasting a different key each time

3. Restart `manager` so it reconnects to the now-unsealed Vault:

       ./docker-auto.sh restart manager

4. Log in with the root token, register the app's policy, and issue a scoped token for the app to use day-to-day instead of the root token — see [Vault tokens, policy & renewal](#vault-tokens-policy--renewal).

### Restarting after a seal (day 2)

Whether Vault is sealed on purpose (`vault operator seal`) or as a side effect of the `vault` container restarting — host reboot, a new image being pulled via `./docker-auto.sh up`, a crash — it always comes back up **sealed**, and `manager` needs to be restarted afterwards to pick up a working connection. Every time this happens, repeat steps 2 and 3 above:

    ./docker-auto.sh vault-unseal   # x3, with 3 of the 5 unseal keys
    ./docker-auto.sh restart manager

To seal Vault deliberately (e.g. before maintenance):

    ./docker-auto.sh vault-cmd operator seal

### Vault tokens, policy & renewal

The root token issued by `vault operator init` should never be used by the app day-to-day — create a scoped token instead.

Register the app's policy (defined in [vault-config/base-policy.hcl](vault-config/base-policy.hcl)):

    ./docker-auto.sh vault-cmd policy write base /vault/config/base-policy.hcl

Create a new orphan token with that policy:

    ./docker-auto.sh vault-cmd token create -policy=base -orphan

Take note of the new token and set it as `VAULT_TOKEN` (in `local_settings.py`, or as the `VAULT_TOKEN` environment variable).

Tokens have an expiry — check it with:

    ./docker-auto.sh vault-cmd token lookup

The `ttl` and `expire_time` fields tell you how much time is left; renew before it runs out. Renew for another month at a time:

    ./docker-auto.sh vault-cmd token renew -increment=750h

There's also a shortcut that logs in and renews the token currently set in `.env` in one go:

    ./docker-auto.sh vault-renew

## docker-auto.sh command reference

By default, commands run against production (`common-service.yml` + `docker-compose.yml`). Pass `--dev` to run against the dev stack (`docker-compose-dev.yml`) instead — there is no `--prod` flag, production is just the default.

| Command                       | What it does                                                      |
|--------------------------------|---------------------------------------------------------------------|
| `up`                           | Pull, build, and (re)start all services                             |
| `down` / `ps` / `restart ...`  | Passed straight through to `docker-compose`                         |
| `logs [service]`                | Follow logs (last 200 lines)                                        |
| `login`                        | `docker login` to `$REGISTRY_URL`                                   |
| `vault-init`                    | Run `vault operator init`                                            |
| `vault-unseal`                  | Run `vault operator unseal` (needs 3 of the 5 keys, one per call)    |
| `vault-login`                   | Run `vault login`                                                    |
| `vault-renew`                   | Log in and renew the token from `.env` for another 750h              |
| `vault-cmd <args>`              | Run an arbitrary `vault` CLI command inside the container            |
| `stop-all` / `remove-all`       | Stop / remove *all* containers on the host (not scoped to this stack)|
| `flush`                         | Run `pwd-manager-auto.sh flush` inside the `manager` container       |

## Korean translation

A Korean translation of this document is planned as a follow-up once the English version above is finalized.
