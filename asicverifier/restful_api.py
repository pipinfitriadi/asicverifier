#!/usr/bin/env python3

# This module is part of AsicVerifier and is released under
# the AGPL-3.0-only License: https://opensource.org/license/agpl-v3/

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from . import META_DATA, SUMMARY


def restful_api(
    path: str = '/',
    host: str = '0.0.0.0',
    port: int = 80
):
    'RESTful API'

    path = path[:-1] if path.endswith('/') else path
    api: FastAPI = FastAPI(
        title=SUMMARY,
        version=META_DATA['Version'],
        docs_url=f'{path}/docs',
        redoc_url=f'{path}/redoc',
        openapi_url=f'{path}/openapi.json'
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
    api.include_router(router, prefix=path)
    uvicorn.run(api, host=host, port=port)
