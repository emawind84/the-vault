#!/usr/bin/env bash

set -e

###############################################
# Extract Environment Variables from .env file
# Ex. REGISTRY_URL="$(getenv REGISTRY_URL)"
###############################################
getenv(){
    local _env="$(printenv $1)"
    echo "${_env:-$(cat .env | awk 'BEGIN { FS="="; } /^'$1'/ {sub(/\r/,"",$2); print $2;}')}"
}

DOCKER_COMPOSE_VERSION="1.14.0"
CONF_ARG="-f common-service.yml -f docker-compose.yml"
SCRIPT_BASE_PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
REGISTRY_URL="$(getenv REGISTRY_URL)"

cd "$SCRIPT_BASE_PATH"

########################################
# Install docker-compose
# DOCKER_COMPOSE_VERSION need to be set
########################################
install_docker_compose() {
    sudo curl -L "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    return 0
}

if ! command -v docker-compose >/dev/null 2>&1; then
    install_docker_compose
elif [[ "$(docker-compose version --short)" != "$DOCKER_COMPOSE_VERSION" ]]; then
    install_docker_compose
fi

usage() {
echo "Usage:  $(basename "$0") [MODE] [OPTIONS] [COMMAND]"
echo
echo "Mode:"
echo "  --prod          Production mode"
echo "  --dev           Development mode"
echo
echo "Options:"
echo "  --help            Show this help message"
echo
echo "Commands:"
echo "  up              Start the services"
echo "  down            Stop the services"
echo "  dump            Create a DB dump file"
echo "  ps              Show the status of the services"
echo "  logs            Follow the logs on console"
echo "  login           Log in to a Docker registry"
echo "  vault-init      Initialize the vault"
echo "  vault-unseal    Unseal the vault"
echo "  vault-seal      Seal the vault"
echo "  vault-login     Log in into the vault"
echo "  stop-all        Stop all containers running"
}

if [ $# -eq 0 ]; then
    usage
    exit 1
fi

for i in "$@"; do
    case $i in
        --dev)
            CONF_ARG="-f docker-compose-dev.yml"
            shift
            ;;
        --help|-h)
            usage
            exit 1
            ;;
        *)
            ;;
    esac
done

echo "Arguments: $CONF_ARG"
echo "Command: $@"

if [ "$1" == "login" ]; then
    docker login $REGISTRY_URL
    exit 0

elif [ "$1" == "up" ]; then
    docker-compose $CONF_ARG pull
    docker-compose $CONF_ARG build --pull
    docker-compose $CONF_ARG up -d --remove-orphans
    exit 0

elif [ "$1" == "stop-all" ]; then
    if [ -n "$(docker ps --format {{.ID}})" ]
    then docker stop $(docker ps --format {{.ID}}); fi
    exit 0

elif [ "$1" == "remove-all" ]; then
    if [ -n "$(docker ps -a --format {{.ID}})" ]
    then docker rm $(docker ps -a --format {{.ID}}); fi
    exit 0

elif [ "$1" == "logs" ]; then
    shift
    docker-compose $CONF_ARG logs -f --tail 200 "$@"
    exit 0

elif [ "$1" == "vault-init" ]; then
    shift
    docker-compose $CONF_ARG exec vault vault operator init
    exit 0

elif [ "$1" == "vault-unseal" ]; then
    shift
    docker-compose $CONF_ARG exec vault vault operator unseal
    exit 0

elif [ "$1" == "vault-login" ]; then
    shift
    docker-compose $CONF_ARG exec vault vault login
    exit 0

elif [ "$1" == "flush" ]; then
    shift
    docker-compose $CONF_ARG exec manager pwd-manager-auto.sh flush
    exit 0

fi

docker-compose $CONF_ARG "$@"

