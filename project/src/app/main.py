from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routes import aemet_routes, db_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(aemet_routes.router, prefix="/api/aemet")
app.include_router(db_routes.router, prefix="/api/db")