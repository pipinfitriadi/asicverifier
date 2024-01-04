#!/usr/bin/env python3

# Copyright (C) Free Software Foundation, Inc. All rights reserved.
# Licensed under the AGPL-3.0-only License. See LICENSE in the project root
# for license information.

import logging
from os import getenv

from typer import Typer

from . import SUMMARY
from .restful_api import RestfulApi

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
cli: Typer = Typer(
    help=SUMMARY,
    add_completion=False,
    pretty_exceptions_show_locals={
        'true': True, 'false': False
    }.get(getenv('DEV_MODE'), False)
)

for command in [
    RestfulApi.run
]:
    cli.command()(command)

if __name__ == '__main__':
    cli()  # pragma: no cover
