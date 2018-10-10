FROM alpine:3.8

COPY . /opt/pwd-manager
WORKDIR /opt/pwd-manager

ENV PYTHON_ENV=/opt/python \
    MANAGER_PATH=/opt/pwd-manager \
    ALLOWED_HOSTS=0.0.0.0

ENV PATH=$PATH:$PYTHON_ENV/bin:$MANAGER_PATH

RUN set -e && \
    apk add --no-cache \
        bash \
        python3 \
        #libldap \
        openldap-dev \
        py-pip && \
    pip install --upgrade pip && \
    pip install virtualenv

RUN set -e && \
    apk add --no-cache --virtual .build-deps \
        build-base \
        python3-dev && \
    virtualenv $PYTHON_ENV --python=python3 && \
    . $PYTHON_ENV/bin/activate && \
    pip install -r requirements.txt && \
    deactivate && \
    apk del .build-deps

EXPOSE 8091

VOLUME [ "$MANAGER_PATH/data", "$MANAGER_PATH/static" ]

RUN chmod +x $MANAGER_PATH/pwd-manager-auto.sh
#CMD [ "pwd-manager-auto.sh" ]
ENTRYPOINT ["bash", "pwd-manager-auto.sh"]