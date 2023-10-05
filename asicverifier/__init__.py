#!/usr/bin/env python3

# This module is part of AsicVerifier and is released under
# the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/

from dateutil import tz
from dateutil.parser import parse
from datetime import datetime
from enum import Enum
from io import BytesIO
import logging
import re
from os import getenv
from os.path import isdir
import subprocess
from tempfile import NamedTemporaryFile
from urllib.parse import urlencode, urljoin, urlparse
from zipfile import ZipFile

from dotenv import load_dotenv
from importlib_metadata import PackageMetadata, metadata
import requests

load_dotenv()
META_DATA: PackageMetadata = metadata(__name__)
SUMMARY: str = META_DATA['Summary']


def to_datetime(string: str) -> datetime:
    return parse(string, tzinfos={'WIB': tz.gettz('Asia/Jakarta')})


def extract_subject_or_issuer(message: str) -> dict:
    return dict([
        element.split('=')
        for element in message.split(', ')
    ])


def extract_asice(message: str) -> dict:
    return {
        'verification': re.search(
            r'Verification (\w+)\.', message
        ).group(1),
        **{
            parent: {
                eldest_children: {
                    'subject': subject,
                    'issuer': issuer,
                    'serial_number': serial_number,
                    'valid': {'from': valid_from, 'until': valid_until}
                },
                **youngest_child
            }
            for (
                (parent, eldest_children),
                (subject, issuer, serial_number, valid_from, valid_until),
                youngest_child
            ) in zip(
                (
                    ('signer', 'certificate'),
                    ('ocsp_response', 'signed_by'),
                    ('timestamp', 'signed_by')
                ),
                zip(
                    map(
                        extract_subject_or_issuer,
                        re.findall(
                            r'Subject: (.+)\s+', message
                        )
                    ),
                    map(
                        extract_subject_or_issuer,
                        re.findall(
                            r'Issuer: (.+)\s+', message
                        )
                    ),
                    map(
                        int,
                        re.findall(
                            r'Serial number: (.+)\s+', message
                        )
                    ),
                    map(
                        to_datetime,
                        re.findall(
                            r'Valid from: (.+)\s+', message
                        )
                    ),
                    map(
                        to_datetime,
                        re.findall(
                            r'Valid until: (.+)\s+', message
                        )
                    )
                ),
                (
                    {
                        'id': {
                            key.lower(): value
                            for key, value in [
                                re.search(
                                    r'ID: (.+)\s+', message
                                ).group(1).split(':')
                            ]
                        }
                    },
                    {
                        'produced_at': to_datetime(
                            re.search(
                                r'Produced at: (.+)\s+', message
                            ).group(1)
                        )
                    },
                    {
                        'date': to_datetime(
                            re.search(r'Date: (.+)\s+', message).group(1)
                        )
                    }
                )
            )
        },
        'file': [
            {'path': path, 'digist': digist, 'status': status}
            for path, digist, status in re.findall(
                r'digest for \"(.+)\" is: (.+) \((.+)\)', message
            )
        ]
    }


class AsiceType(str, Enum):
    REQUEST: str = 'request'
    RESPONSE: str = 'response'


def asicverifier(
    security_server_url: str,
    query_id: str,
    x_road_instance: str,
    member_class: str,
    member_code: str,
    subsystem_code: str,
    asice_type: AsiceType = AsiceType.REQUEST,
    conf_refresh: bool = None
) -> dict:
    CONF_PATH: str = (
        f'asicverifier/security-server/{urlparse(security_server_url).netloc}/'
    )

    if conf_refresh or not isdir(CONF_PATH):
        # Zip File
        response = requests.get(
            urljoin(security_server_url, 'verificationconf'),
            allow_redirects=True
        )

        try:
            response.raise_for_status()

            with ZipFile(BytesIO(response.content)) as zip_file:
                zip_file.extractall(CONF_PATH)
        except requests.exceptions.HTTPError:
            logging.error(f"verificationconf: '{response.text}'")
            raise

    # Asice File
    response = requests.get(
        '{url}?unique&{asice_type}&{params}'.format(
            url=urljoin(security_server_url, 'asic'),
            asice_type={
                enum.value: f'{enum.value}Only'
                for enum in AsiceType
            }[asice_type.value],
            params=urlencode({
                'queryId': query_id,
                'xRoadInstance': x_road_instance,
                'memberClass': member_class,
                'memberCode': member_code,
                'subsystemCode': subsystem_code
            })
        ),
        allow_redirects=True
    )

    try:
        response.raise_for_status()

        with NamedTemporaryFile() as temp, subprocess.Popen(
                ['yes', 'n'], stdout=subprocess.PIPE) as proc_yes:
            temp.write(response.content)
            temp.seek(0)
            message: str = subprocess.run(
                [
                    'java', '-jar',
                    getenv('JAR_PATH', '/lib/asicverifier.jar'),
                    f'{CONF_PATH}/verificationconf/',
                    temp.name
                ],
                stdin=proc_yes.stdout,
                capture_output=True
            ).stdout.decode()
            proc_yes.kill()
            logging.debug(message)
    except requests.exceptions.HTTPError:
        logging.error(f"Asice: '{response.text}'")
        raise

    return extract_asice(message)
