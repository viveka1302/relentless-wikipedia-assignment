from fastapi import FastAPI
#from .settings import SWAGGER_URL, REDOC_URL, APP_NAME
from fastapi.middleware.cors import CORSMiddleware

tags_metadata = [
    {
        "name": 'relentless-wikipedia',
        "description": "APIs to search and tag wikipedia articles"
    }
]
app= FastAPI(openapi_tags=tags_metadata )#redoc_url=REDOC_URL, docs_url=SWAGGER_URL

origins = ["*"]


app.add_middleware(


    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
