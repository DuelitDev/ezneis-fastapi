import ezneis
import ezneis.exceptions
import uvicorn
from datetime import datetime
from fastapi import FastAPI, HTTPException
from os import environ

VERSION = "1.0.0"
KEY = environ.get("NEIS_OPEN_API_KEY", "")
PORT = int(environ.get("PORT", 8080))
app = FastAPI()

BREAKFASTS = 8 * 3600 + 10 * 60  # 8:10
LUNCHES = 13 * 3600 + 10 * 60  # 13:10
DINNERS = 18 * 3600 + 10 * 60  # 18:10


@app.get("/version")
async def endpoint_version():
    return {"version": VERSION}


@app.get("/today")
async def endpoint_today(code: str):
    data = ezneis.get_school(KEY, code)
    date = datetime.today().strftime("%Y%m%d")
    data.load_meals(date=date)
    return data.meals


@app.get("/auto")
async def endpoint_auto(code: str):
    meals = await endpoint_today(code)
    today = datetime.today()
    today_sec = today.hour * 3600 + today.minute * 60 + today.second
    match today_sec:
        case s if s < BREAKFASTS:
            meals = meals.breakfasts
        case s if s < LUNCHES:
            meals = meals.lunches
        case s if s < DINNERS:
            meals = meals.dinners
        case _:
            return tuple()
    return meals


@app.exception_handler(ezneis.exceptions.DataNotFoundException)
async def data_not_found_exception_handler(request, exc):
    raise HTTPException(status_code=404, detail="Data Not Found.")


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    raise HTTPException(status_code=500, detail="Unknown Error.")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
