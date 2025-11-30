from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.user_position_router import user_positions_router
from routers.estimation_router import estimation_router
from routers.date_router import date_router

app = FastAPI()

origins = [
    "http://localhost:4173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_positions_router, prefix="/users", tags=["User Positions"])
app.include_router(estimation_router, prefix="/estimator", tags=["Estimator"])
app.include_router(date_router, prefix="/datetime", tags=["Date Time"])

@app.get("/")
def root():
    return {"message": "Service running"}