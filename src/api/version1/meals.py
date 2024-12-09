import ezneis
from ..common import *
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from typing import Literal

__all__ = [
    "app"
]

BREAKFASTS = 8 * 3600 + 10 * 60   # 8:10
LUNCHES    = 13 * 3600 + 10 * 60  # 13:10
DINNERS    = 18 * 3600 + 10 * 60  # 18:10


def get_today_sec() -> int:
    today = datetime.today()
    return today.hour * 3600 + today.minute * 60 + today.second


def get_app_time_from(meals, time: Literal["breakfasts", "lunches", "dinners"]):
    match time:
        case "breakfasts": return meals.breakfasts
        case "lunches":    return meals.lunches
        case "dinners":    return meals.dinners
        case _: raise HTTPException(status_code=400, detail="Invalid time.")


def get_app_now_from(meals):
    sec = get_today_sec()
    match sec:
        case sec if sec < BREAKFASTS: return meals.breakfasts
        case sec if sec < LUNCHES:    return meals.lunches
        case sec if sec < DINNERS:    return meals.dinners
    return tuple()



app = FastAPI()


@app.get("/")
async def root():
    data = await ezneis.get_school_async(KEY, NAME)
    return await data.meals


@app.get("/all")
async def app_all():
    return await root()


@app.get("/all/{time}")
async def app_all_time(
        time: Literal["breakfasts", "lunches", "dinners"]):
    return get_app_time_from(await root(), time)


@app.get("/today")
async def app_today():
    data = await ezneis.get_school_async(KEY, NAME)
    date = datetime.today().strftime("%Y%m%d")
    await data.load_meals(date=date)
    return await data.meals


@app.get("/today/now")
async def app_today_now():
    return get_app_now_from(await app_today())


@app.get("/today/{time}")
async def app_today_time(
        time: Literal["breakfasts", "lunches", "dinners"]):
    return get_app_time_from(await app_today(), time)


@app.get("/auto")
async def app_auto():
    data = await ezneis.get_school_async(KEY, NAME)
    today = datetime.today()
    weekday = today.weekday()
    if 4 < weekday:  # if today is weekend
        monday = today + timedelta(days=7 - weekday)  # get next monday
        date = monday.strftime("%Y%m%d")
        await data.load_meals(date=date)
        return await data.meals
    elif get_today_sec() >= DINNERS:
        tomorrow = today + timedelta(days=1)  # get tomorrow
        date = tomorrow.strftime("%Y%m%d")
        await data.load_meals(date=date)
        return await data.meals
    else:
        return (await data.meals).today


@app.get("/auto/now")
async def app_auto_now():
    return get_app_now_from(await app_auto())


@app.get("/auto/{time}")
async def app_auto_time(
        time: Literal["breakfasts", "lunches", "dinners"]):
    return get_app_time_from(await app_auto(), time)


@app.get("/{weekday}")
async def app_weekday(
        weekday: Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]):
    data = await ezneis.get_school_async(KEY, NAME)
    today = datetime.today()
    match weekday:
        case "mon": target = today + timedelta(0 - today.weekday())
        case "tue": target = today + timedelta(1 - today.weekday())
        case "wed": target = today + timedelta(2 - today.weekday())
        case "thu": target = today + timedelta(3 - today.weekday())
        case "fri": target = today + timedelta(4 - today.weekday())
        case "sat": target = today + timedelta(5 - today.weekday())
        case "sun": target = today + timedelta(6 - today.weekday())
        case _: raise HTTPException(status_code=400, detail="Invalid weekday.")
    date = target.strftime("%Y%m%d")
    await data.load_meals(date=date)
    return await data.meals


@app.get("/{weekday}/{time}")
async def app_weekday_time(
        weekday: Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        time: Literal["breakfasts", "lunches", "dinners"]):
    return get_app_time_from(await app_weekday(weekday), time)


if __name__ == "__main__":
    raise EnvironmentError("This module cannot be run directly.")
