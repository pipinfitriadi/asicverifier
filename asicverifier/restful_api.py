#!/usr/bin/env python3

# This module is part of AsicVerifier and is released under
# the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/

from datetime import datetime
from os import getenv
from typing import List, Union

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import (
    BaseModel,
    DirectoryPath,
    EmailStr,
    Field,
    FilePath,
    NonNegativeInt
)
import uvicorn

from . import asicverifier, META_DATA, SUMMARY


class AsicSignerId(BaseModel):
    subsystem: DirectoryPath


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
    path: FilePath
    digist: str
    status: str


class Asic(BaseModel):
    verification: str
    signer: AsicSigner
    ocsp_response: AsicOcspResponse
    timestamp: AsicTimeStamp
    file: List[AsicFile]


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
        router.get(
            '/', name='verifier', response_model=Union[Asic, dict]
        )(asicverifier)

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
