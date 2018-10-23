# THE VAULT

A web application for managing credentials.

HashiCorp Vault is required for securely store the credentials.

## Set up the project

Upgrade pip to the latest version:

`python -m pip upgrade pip`

Then we install virtualenv:

`pip install --user virtualenv`

With the next command we create a new python environment, using python version 3, so we can install the required modules without creating issues to other python applications:

`virtualenv env --python=python3`

if everything is ok you will see a new folder `env` inside the project folder.

In order to work in our new environment we need to activate it:

`source env/bin/activate`

We should see an `(env)` at the start of the command line

Now we are ready to install the required modules:

`pip install -r requirements.txt`

Before starting the application we initialize the database:

`python manage.py migrate`

We create a superuser for managing users and groups:

`python manage.py createsuperuser`

Before starting the application some configuration is required, create a new file named `local.settings.py` into the `pwd_manager` folder, just near the `settings.py` and add all the required variables.

The following variables should be passed to the application, through the `local.settings.py` or as `shell variables`:

    VAULT_HOST
    VAULT_TOKEN

The vault token is created the first time the vault is initialized, so you need to run the server and then initialized it:

    $ vault operator init

The output of this command should give you five unseal keys and one initial root token to use to log in into the vault.

Now we are ready to run the application:

    $ ./pwd-manager-auto.sh

## Production

Before running the application in production, we should create a new `SECRET_KEY`, for security reason,
we can use the function `django.core.management.utils.get_random_secret_key()`.

The variable `DEBUG` should be set to `False`.

Also we need to collect the static files since django will refuse to serve static files with `DEBUG=False`; we will use the command `collectstatic` provided by django:

    $ python manage.py collectstatic --clear

A new folder `static` should be created under the project folder.

In the web server configuration we need to add the static location in order to serve those files:

    location /static/ {
        root /media/usb2/pwd_manager;
    }

### Token Creation

A new vault token should be generated to log in and access the secrets through the manager, the root token should not be used for security reason.

A policy to use can be found in the folder vault-config, `base-policy.hcl`.

We need to register this policy first, and then create a new token with this policy associated:

    $ vault policy write base vault-config/base-policy
    $ vault token create -policy=base -orphan

take note of the new token and update the variable `VAULT_TOKEN` with the new value.


## Execution with Docker

If Docker is used the vault commands can still be executed:

    $ ./docker-auto.sh vault-cmd <vault command here> <args>

To register the policy you can run the following command:

    $ ./docker-auto.sh vault-cmd policy write base /vault/config/base-policy.hcl