#!/usr/bin/env python3

# This module is part of AsicVerifier and is released under
# the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/

import logging
from os import getenv

from dotenv import load_dotenv
from typer import Typer

from . import META_DATA

load_dotenv()
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
cli: Typer = Typer(
    help=META_DATA['Summary'],
    add_completion=False,
    pretty_exceptions_show_locals={
        'true': True, 'false': False
    }.get(getenv('DEV_MODE'), False)
)

for command in [
    lambda: None
]:
    cli.command()(command)

if __name__ == '__main__':
    cli()
