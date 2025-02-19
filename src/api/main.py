from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import db_routes
from helpers.config import api_url, streamlit_url

app = FastAPI(title="Proyecto Meteorológico API", docs_url="/api/docs", openapi_url="/api/openapi.json")

# noinspection PyTypeChecker,PydanticTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=[api_url, streamlit_url],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Accept-Encoding",
        "Accept-Language",
        "Origin",
        "Referer",
        "User-Agent",
        "Cache-Control",
        "Access-Control-Allow-Origin",
    ],
)


@app.get("/")
def read_root():
    return {
        "Site": f"{streamlit_url}",
        "Docs": f"{api_url}/docs"
    }


app.include_router(db_routes.router, prefix="/api/db")
