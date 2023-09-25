# This file is part of DataSae and is released under
# the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/

FROM python:3.7-alpine
LABEL maintainer='pipinfitriadi@gmail.com'
COPY --from=niis/xroad-security-server-sidecar:7.0.4 /usr/share/xroad/jlib/asicverifier.jar /opt/
ENV JAVA_HOME=/opt/java/openjdk
COPY --from=eclipse-temurin:8-alpine $JAVA_HOME $JAVA_HOME
ENV PATH="${JAVA_HOME}/bin:${PATH}"
ENTRYPOINT [ "java", "-jar", "/opt/asicverifier.jar"]
