#!/usr/bin/env python3

# This module is part of AsicVerifier and is released under
# the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/

from datetime import datetime
from os import getenv
from typing import Any, List

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    HttpUrl,
    NonNegativeInt
)
import uvicorn

from . import AsiceType, asicverifier, META_DATA, SUMMARY


class AsicSignerId(BaseModel):
    subsystem: str


class AsicSignValid(BaseModel):
    from_: datetime = Field(alias='from')
    until: datetime


class AsicOcsp(BaseModel):
    CN: str
    O: str


class AsicSign(BaseModel):
    subject: AsicOcsp
    issuer: AsicOcsp
    serial_number: NonNegativeInt
    valid: AsicSignValid


class AsicSignerCertificateSubject(AsicOcsp):
    C: str


class AsicSignerCertificate(AsicSign):
    subject: AsicSignerCertificateSubject


class AsicSigner(BaseModel):
    certificate: AsicSignerCertificate
    id: AsicSignerId


class AsicOcspResponse(BaseModel):
    signed_by: AsicSign
    produced_at: datetime


class AsicTimeStampSignByIssuer(AsicSignerCertificateSubject, BaseModel):
    ST: str
    L: str
    EMAILADDRESS: EmailStr
    OU: str


class AsicTimeStampSignBySubject(AsicTimeStampSignByIssuer):
    oid_2_5_4_13: str = Field(alias='OID.2.5.4.13')


class AsicTimeStampSignBy(AsicSign):
    subject: AsicTimeStampSignBySubject
    issuer: AsicTimeStampSignByIssuer


class AsicTimeStamp(BaseModel):
    signed_by: AsicTimeStampSignBy
    date: datetime


class AsicFile(BaseModel):
    path: str
    digist: str
    status: str


class Asice(BaseModel):
    verification: str
    signer: AsicSigner
    ocsp_response: AsicOcspResponse
    timestamp: AsicTimeStamp
    file: List[AsicFile]


StringNoneEmptySpace: Any = Field(pattern=r'^[\w\-]+$')


class AsicVerifier(BaseModel):
    security_server_url: HttpUrl
    query_id: str = StringNoneEmptySpace
    x_road_instance: str = StringNoneEmptySpace
    member_class: str = StringNoneEmptySpace
    member_code: str = StringNoneEmptySpace
    subsystem_code: str = StringNoneEmptySpace
    asice_type: AsiceType = AsiceType.REQUEST


class RestfulApi:
    @staticmethod
    def app() -> FastAPI:
        RESTFUL_API_PATH: str = getenv('RESTFUL_API_PATH', '/')

        if RESTFUL_API_PATH.endswith('/'):
            RESTFUL_API_PATH = RESTFUL_API_PATH[:-1]

        api: FastAPI = FastAPI(
            title=SUMMARY,
            version=META_DATA['Version'],
            docs_url=f'{RESTFUL_API_PATH}/docs',
            redoc_url=f'{RESTFUL_API_PATH}/redoc',
            openapi_url=f'{RESTFUL_API_PATH}/openapi.json'
        )
        api.add_middleware(
            CORSMiddleware,
            allow_origins=[
                'http://0.0.0.0',
                'http://localhost',
                'http://localhost:8080'
            ],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*']
        )
        router = APIRouter()

        @router.post('/')
        async def verifier(
            data: AsicVerifier, conf_refresh: bool = None
        ) -> Asice:
            return asicverifier(
                **{
                    key: value if key == 'asice_type' else f'{value}'
                    for key, value in data
                },
                conf_refresh=conf_refresh
            )

        api.include_router(router, prefix=RESTFUL_API_PATH)
        return api

    @staticmethod
    def run(
        host: str = '0.0.0.0', port: int = 80, reload: bool = False
    ):
        'RESTful API'

        uvicorn.run(
            f'{__name__}:RestfulApi.app',
            host=host,
            port=port,
            reload=reload,
            factory=True
        )  # pragma: no cover
