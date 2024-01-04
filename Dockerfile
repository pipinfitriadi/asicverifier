# Copyright (C) Free Software Foundation, Inc. All rights reserved.
# Licensed under the AGPL-3.0-only License. See LICENSE in the project root
# for license information.

FROM python:3.8-alpine AS venv
LABEL maintainer=pipinfitriadi@gmail.com
ADD https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h skipcache
RUN pip install \
        --upgrade \
        --root-user-action=ignore \
        pip && \
    pip install \
        --no-cache-dir \
        --upgrade \
        --root-user-action=ignore \
        --target=/opt/venv/ \
        AsicVerifier[restful-api]

FROM python:3.8-alpine
LABEL maintainer=pipinfitriadi@gmail.com
COPY --from=niis/xroad-security-server-sidecar:7.0.4 /usr/share/xroad/jlib/asicverifier.jar /lib/
ENV JAVA_HOME /opt/java/openjdk
COPY --from=eclipse-temurin:8-alpine $JAVA_HOME $JAVA_HOME
ENV PATH $JAVA_HOME/bin:$PATH
COPY --from=venv /opt/venv/ /opt/venv/
ENV PYTHONPATH $PYTHONPATH:/opt/venv/
ENTRYPOINT /opt/venv/bin/asicverifier
