from fastapi import FastAPI
from api.version1.main import app as v1


__version__ = "0.1.2"
app = FastAPI()


@app.get("/")
async def root():
    return {"version": __version__}


@app.get("/version")
async def version():
    return {"version": __version__}


app.mount("/v1", v1)
