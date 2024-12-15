import ezneis
from ..common import *
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal

__all__ = [
    "app"
]


# region models implementation

class Dish(BaseModel):
    name: str
    allergies: tuple[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                             12, 13, 14, 15, 16, 17, 18, 19], ...]


class Nutrient(BaseModel):
    name: str
    unit: str = "mg"
    value: float


class Origin(BaseModel):
    name: str
    origin: str


class Meal(BaseModel):
    time: Literal[1, 2, 3]
    date: str = "2025-01-01"
    headcount: int
    dishes: tuple[Dish, ...]
    origins: tuple[Origin, ...]
    kcal: float
    nutrients: tuple[Nutrient, ...]

# endregion


# region utilities implementation

BREAKFASTS = 8 * 3600 + 10 * 60   # 8:10
LUNCHES    = 13 * 3600 + 10 * 60  # 13:10
DINNERS    = 18 * 3600 + 10 * 60  # 18:10


def get_today_sec() -> int:
    today = datetime.today()
    return today.hour * 3600 + today.minute * 60 + today.second


def only_one(it):
    if len(it) == 1:
        return it[0]
    return type(it)()


def get_app_time_from(meals, time: Literal["breakfasts", "lunches", "dinners"]):
    match time:
        case "breakfasts": return meals.breakfasts
        case "lunches":    return meals.lunches
        case "dinners":    return meals.dinners
        case _: raise HTTPException(status_code=400, detail="Invalid time.")

# endregion


# region endpoint implementation

app = FastAPI()


# noinspection SpellCheckingInspection
@app.get("/", response_model=list[Meal])
async def root():
    """
    이번 주의 모든 급식 식단 정보를 반환합니다.
    """
    data = await ezneis.get_school_async(KEY, NAME)
    return await data.meals


# noinspection SpellCheckingInspection
@app.get("/all", response_model=list[Meal])
async def app_all():
    """
    이번 주의 모든 급식 식단 정보를 반환합니다.
    """
    return await root()


# noinspection SpellCheckingInspection
@app.get("/all/{time}", response_model=list[Meal])
async def app_all_time(
        time: Literal["breakfasts", "lunches", "dinners"]):
    """
    이번 주의 특정 시간의 급식 식단 정보를 반환합니다.
    """
    return get_app_time_from(await root(), time)


# noinspection SpellCheckingInspection
@app.get("/today", response_model=list[Meal])
async def app_today():
    """
    오늘의 급식 식단 정보를 반환합니다.
    """
    data = await ezneis.get_school_async(KEY, NAME)
    date = datetime.today().strftime("%Y%m%d")
    await data.load_meals(date=date)
    return await data.meals


# noinspection SpellCheckingInspection
@app.get("/today/now", response_model=list[Meal])
async def app_today_now():
    """
    현재 시각에 알맞은 급식 식단 정보를 반환합니다.

    이 엔드포인트는 한 개 이하의 데이터를 반환함을 보장합니다.
    """
    meals = await app_today()
    sec = get_today_sec()
    match sec:
        case sec if sec < BREAKFASTS: meals = meals.breakfasts
        case sec if sec < LUNCHES:    meals = meals.lunches
        case sec if sec < DINNERS:    meals = meals.dinners
        case _:                       meals = tuple()
    return only_one(meals)


# noinspection SpellCheckingInspection
@app.get("/today/{time}", response_model=list[Meal])
async def app_today_time(
        time: Literal["breakfasts", "lunches", "dinners"]):
    """
    오늘의 특정 시각의 급식 식단 정보를 반환합니다.

    이 엔드포인트는 한 개 이하의 데이터를 반환함을 보장합니다.
    """
    return only_one(get_app_time_from(await app_today(), time))


# noinspection SpellCheckingInspection
@app.get("/auto", response_model=list[Meal])
async def app_auto():
    """
    적절한 날의 급식 식단 정보를 반환합니다.

    가령, 오늘이 주말인 경우 다음 주 월요일의 급식 식단 정보를 반환하고,
    현재 시각이 저녁 시간을 지난 경우 익일의 급식 식단 정보를 반환합니다
    (단, 금요일인 경우 다음 주 월요일의 급식 식단 정보를 반환합니다).
    이외의 경우에는 오늘의 급식 식단 정보를 반환합니다.
    """
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
        if 4 < tomorrow.weekday():  # if today is friday
            tomorrow = today + timedelta(days=3)  # get next monday
        date = tomorrow.strftime("%Y%m%d")
        await data.load_meals(date=date)
        return await data.meals
    else:
        return (await data.meals).today


# noinspection SpellCheckingInspection
@app.get("/auto/now", response_model=list[Meal])
async def app_auto_now():
    """
    적절한 날의 시각에 알맞은 급식 식단 정보를 반환합니다.

    가령, 오늘이 주말인 경우 다음 주 월요일의 아침 급식 식단 정보를 반환하고,
    현재 시각이 저녁 시간을 지난 경우 익일의 아침 급식 식단 정보를 반환합니다
    (단, 금요일인 경우 다음 주 월요일의 아침 급식 식단 정보를 반환합니다).
    이외의 경우에는 현재 시각에 알맞은 급식 식단 정보를 반환합니다.

    이 엔드포인트는 한 개 이하의 데이터를 반환함을 보장합니다.
    """
    meals = await app_auto()
    if len(meals) == 0:  # if there is no data
        return tuple()
    today = datetime.today().date()
    if not meals[0].date == today:  # if data is not today's data
        return only_one(meals.breakfasts)
    sec = get_today_sec()
    match sec:
        case sec if sec < BREAKFASTS: meals = meals.breakfasts
        case sec if sec < LUNCHES:    meals = meals.lunches
        case sec if sec < DINNERS:    meals = meals.dinners
        case _:                       meals = tuple()
    return only_one(meals)


# noinspection SpellCheckingInspection
@app.get("/auto/{time}", response_model=list[Meal])
async def app_auto_time(
        time: Literal["breakfasts", "lunches", "dinners"]):
    """
    적절한 날의 특정 시각의 급식 식단 정보를 반환합니다.

    가령, 오늘이 주말인 경우 다음 주 월요일의 특정 시각의 급식 식단 정보를 반환하고,
    현재 시각이 저녁 시간을 지난 경우 익일의 특정 시각의 급식 식단 정보를 반환합니다
    (단, 금요일인 경우 다음 주 월요일의 특정 시각의 급식 식단 정보를 반환합니다).
    이외의 경우에는 오늘의 특정 시각의 급식 식단 정보를 반환합니다.

    이 엔드포인트는 한 개 이하의 데이터를 반환함을 보장합니다.
    """
    return only_one(get_app_time_from(await app_auto(), time))


# noinspection SpellCheckingInspection
@app.get("/{weekday}", response_model=list[Meal])
async def app_weekday(
        weekday: Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]):
    """
    이번 주의 특정 요일의 급식 식단 정보를 반환합니다.
    """
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


# noinspection SpellCheckingInspection
@app.get("/{weekday}/{time}", response_model=list[Meal])
async def app_weekday_time(
        weekday: Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        time: Literal["breakfasts", "lunches", "dinners"]):
    """
    이번 주의 특정 요일의 특정 시간의 급식 식단 정보를 반환합니다.

    이 엔드포인트는 한 개 이하의 데이터를 반환함을 보장합니다.
    """
    return only_one(get_app_time_from(await app_weekday(weekday), time))

# endregion


if __name__ == "__main__":
    raise EnvironmentError("This module cannot be run directly.")
