import ezneis
from ..common import *
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from typing import Literal

__all__ = [
    "app"
]


def get_app_grade_from(
        timetables, grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"]):
    match grade:
        case "0": return timetables.grade0
        case "1": return timetables.grade1
        case "2": return timetables.grade2
        case "3": return timetables.grade3
        case "4": return timetables.grade4
        case "5": return timetables.grade5
        case "6": return timetables.grade6
        case "7": return timetables.grade7
        case _: raise HTTPException(status_code=400, detail="Invalid grade.")


def get_app_grade_classname_from(
        timetables, grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"],
        classname: str):
    timetables = get_app_grade_from(timetables, grade)
    return timetables.filter_by_classroom_name(classname)


def get_app_grade_classname_period_from(
        timetables, grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"],
        classname: str, period: Literal["0", "1", "2", "3", "4", "5", "6", "7",
        "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"]):
    timetables = get_app_grade_classname_from(timetables, grade, classname)
    match period:
        case "0":  return timetables.period0
        case "1":  return timetables.period1
        case "2":  return timetables.period2
        case "3":  return timetables.period3
        case "4":  return timetables.period4
        case "5":  return timetables.period5
        case "6":  return timetables.period6
        case "7":  return timetables.period7
        case "8":  return timetables.period8
        case "9":  return timetables.period9
        case "10": return timetables.period10
        case "11": return timetables.period11
        case "12": return timetables.period12
        case "13": return timetables.period13
        case "14": return timetables.period14
        case "15": return timetables.period15
        case "16": return timetables.period16
        case "17": return timetables.period17
        case "18": return timetables.period18
        case "19": return timetables.period19
        case _: raise HTTPException(status_code=400, detail="Invalid period.")


app = FastAPI()


@app.get("/")
async def root():
    data = await ezneis.get_school_async(KEY, NAME)
    return await data.timetables


@app.get("/all")
async def app_all():
    return await root()


@app.get("/all/{grade}")
async def app_all_grade(grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"]):
    return get_app_grade_from(await app_all(), grade)


@app.get("/all/{grade}/{classname}")
async def app_all_grade_classname(
        grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"], classname: str):
    return get_app_grade_classname_from(await app_all(), grade, classname)


@app.get("/all/{grade}/{classname}/{period}")
async def app_all_grade_classname_period(
        grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"], classname: str,
        period: Literal["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                        "11", "12", "13", "14", "15", "16", "17", "18", "19"]):
    return get_app_grade_classname_period_from(
        await app_all(), grade, classname, period)


@app.get("/today")
async def app_today():
    data = await ezneis.get_school_async(KEY, NAME)
    date = datetime.today().strftime("%Y%m%d")
    await data.load_timetable(date=date)
    return await data.timetables


@app.get("/today/{grade}")
async def app_today_grade(
        grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"]):
    return get_app_grade_from(await app_today(), grade)


@app.get("/today/{grade}/{classname}")
async def app_today_grade_classname(
        grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"], classname: str):
    return get_app_grade_classname_from(await app_today(), grade, classname)


@app.get("/today/{grade}/{classname}/{period}")
async def app_today_grade_classname_period(
        grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"], classname: str,
        period: Literal["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                        "11", "12", "13", "14", "15", "16", "17", "18", "19"]):
    return get_app_grade_classname_period_from(
        await app_today(), grade, classname, period)


@app.get("/auto")
async def app_auto():
    data = await ezneis.get_school_async(KEY, NAME)
    date = datetime.today().strftime("%Y%m%d")
    await data.load_timetable(date=date)
    return await data.timetables


@app.get("/auto/{grade}")
async def app_auto_grade(
        grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"]):
    return get_app_grade_from(await app_auto(), grade)


@app.get("/auto/{grade}/{classname}")
async def app_today_grade_classname(
        grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"], classname: str):
    return get_app_grade_classname_from(await app_auto(), grade, classname)


@app.get("/auto/{grade}/{classname}/{period}")
async def app_today_grade_classname_period(
        grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"], classname: str,
        period: Literal["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                        "11", "12", "13", "14", "15", "16", "17", "18", "19"]):
    return get_app_grade_classname_period_from(
        await app_auto(), grade, classname, period)


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
    await data.load_timetable(date=date)
    return await data.timetables


@app.get("/{weekday}/{grade}")
async def app_weekday_grade(
        weekday: Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"]):
    return get_app_grade_from(await app_weekday(weekday), grade)


@app.get("/{weekday}/{grade}/{classname}")
async def app_weekday_grade_classname(
        weekday: Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"], classname: str):
    return get_app_grade_classname_from(
        await app_weekday(weekday), grade, classname)


@app.get("/{weekday}/{grade}/{classname}/{period}")
async def app_weekday_grade_classname_period(
        weekday: Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        grade: Literal["0", "1", "2", "3", "4", "5", "6", "7"], classname: str,
        period: Literal["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                        "11", "12", "13", "14", "15", "16", "17", "18", "19"]):
    return get_app_grade_classname_period_from(
        await app_weekday(weekday), grade, classname, period)


if __name__ == "__main__":
    raise EnvironmentError("This module cannot be run directly.")
