#!/usr/bin/env python3

# This module is part of AsicVerifier and is released under
# the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/

from datetime import datetime
from enum import Enum
import re
from urllib.parse import urlencode, urljoin

from dotenv import load_dotenv
from importlib_metadata import PackageMetadata, metadata

load_dotenv()
META_DATA: PackageMetadata = metadata(__name__)
SUMMARY: str = META_DATA['Summary']


def to_datetime(string: str) -> datetime:
    return datetime.strptime(string, r'%a %b %d %H:%M:%S %Z %Y')


def extract_subject_or_issuer(message: str) -> dict:
    return dict([
        element.split('=')
        for element in message.split(', ')
    ])


def extract_asic(message: str) -> dict:
    return {
        'verification': re.search(
            r'Verification (.+)\.', message
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


class AsicType(str, Enum):
    REQUEST: str = 'request'
    RESPONSE: str = 'response'


def asicverifier(
    security_server_url: str,
    query_id: str,
    x_road_instance: str,
    member_class: str,
    member_code: str,
    subsystem_code: str,
    type: AsicType = AsicType.REQUEST
) -> dict:
    verificationconf_url: str = urljoin(
        security_server_url, 'verificationconf'
    )
    asic_url: str = '{url}?unique&{type}&{params}'.format(
        url=urljoin(security_server_url, 'asic'),
        type={
            enum.value: f'{enum.value}Only'
            for enum in AsicType
        }[type.value],
        params=urlencode({
            'queryId': query_id,
            'xRoadInstance': x_road_instance,
            'memberClass': member_class,
            'memberCode': member_code,
            'subsystemCode': subsystem_code
        })
    )
    return {'verificationconf_url': verificationconf_url, 'asic_url': asic_url}
