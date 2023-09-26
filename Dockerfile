# This file is part of AsicVerifier and is released under
# the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/

FROM python:3.7-alpine AS venv
LABEL maintainer="pipinfitriadi@gmail.com"
RUN pip install \
        --upgrade \
        --root-user-action=ignore \
        pip && \
    pip install \
        --no-cache-dir \
        --upgrade \
        --root-user-action=ignore \
        --target=/opt/venv/ \
        AsicVerifier

FROM python:3.7-alpine
LABEL maintainer='pipinfitriadi@gmail.com'
COPY --from=niis/xroad-security-server-sidecar:7.0.4 /usr/share/xroad/jlib/asicverifier.jar /lib/
ENV JAVA_HOME=/opt/java/openjdk
COPY --from=eclipse-temurin:8-alpine $JAVA_HOME $JAVA_HOME
ENV PATH $JAVA_HOME/bin:$PATH
COPY --from=venv /opt/venv/ /opt/venv/
ENV PYTHONPATH $PYTHONPATH:/opt/venv/
ENTRYPOINT [ "java", "-jar", "/lib/asicverifier.jar"]
