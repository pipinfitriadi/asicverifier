<!--
This file is part of AsicVerifier and is released under
the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/
-->

# AsicVerifier

[![License](https://img.shields.io/github/license/pipinfitriadi/asicverifier?logoColor=black&label=License&labelColor=black&color=brightgreen)](https://github.com/pipinfitriadi/asicverifier/blob/main/LICENSE)
[![Java - Version](https://img.shields.io/badge/8-ED8B00?logo=openjdk&logoColor=ED8B00&label=Java&labelColor=black)](https://openjdk.org/projects/jdk8/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/asicverifier?logo=python&label=Python&labelColor=black)](https://pypi.org/project/asicverifier/)
[![PyPI - Version](https://img.shields.io/pypi/v/asicverifier?logo=pypi&label=PyPI&labelColor=black)](https://pypi.org/project/asicverifier/)
[![Docker Image Size (tag)](https://img.shields.io/docker/image-size/pipinfitriadi/asicverifier/latest?logo=Docker&label=latest&labelColor=black)](https://hub.docker.com/r/pipinfitriadi/asicverifier)
[![GitHub Action](https://img.shields.io/github/actions/workflow/status/pipinfitriadi/asicverifier/ci-cd.yml?logo=GitHub&label=CI/CD&labelColor=black)](https://github.com/pipinfitriadi/asicverifier/actions/workflows/ci-cd.yml)
[![Codecov](https://img.shields.io/codecov/c/github/pipinfitriadi/asicverifier?logo=codecov&label=Coverage&labelColor=black)](https://app.codecov.io/github/pipinfitriadi/asicverifier)

Asic Verifier for X-Road

> **Note**
>
> This service require [Docker](https://docs.docker.com/get-docker/)

## Environment

| Name               | Type             | Default                 |
|--------------------|------------------|-------------------------|
| `RESTFUL_API_PATH` | String URL Path  | `/`                     |
| `JAR_PATH`         | String File Path | `/lib/asicverifier.jar` |
| `DEV_MODE`         | Bool             | `false`                 |

## Docker

- Start up:

    ```sh
    docker run -d --rm --platform linux/amd64 -p '80:80' --name asicverifier pipinfitriadi/asicverifier
    ```

    > RESTful API's docs should be available at [http://0.0.0.0/docs](http://0.0.0.0/docs)

- Shut down:

    ```sh
    docker stop asicverifier
    ```

- Help:

    ```sh
    docker run --rm --platform linux/amd64 pipinfitriadi/asicverifier --help
    ```

## Docker Compose

`docker-compose.yml`:

```yml
version: '3.7'
services:
asicverifier:
    image: pipinfitriadi/asicverifier
    container_name: asicverifier
    platform: linux/amd64
    ports:
        - '80:80'
```

- Start up:

    ```sh
    docker compose up -d
    ```

    > RESTful API's docs should be available at [http://0.0.0.0/docs](http://0.0.0.0/docs)

- Shut down:

    ```sh
    docker compose down
    ```

- Help:

    ```sh
    docker compose run --rm asicverifier --help && docker compose down
    ```
