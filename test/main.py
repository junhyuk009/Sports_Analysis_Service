from fastapi import FastAPI
from routers import perso

app = FastAPI(title="Football Dubbing API")
app.include_router(perso.router, prefix="/api/perso", tags=["Perso API"])
