import ezneis
import ezneis.exceptions
import functions_framework
from datetime import datetime
from dataclasses import asdict
from orjson import dumps
from os import environ

VERSION = "1.0.0"
KEY = environ["NEIS_OPEN_API_KEY"]
BREAKFASTS = 8 * 3600 + 10 * 60   # 8:10
LUNCHES    = 13 * 3600 + 10 * 60  # 13:10
DINNERS    = 18 * 3600 + 10 * 60  # 18:10


def to_json(models):
    return dumps([asdict(model) for model in models]).decode("utf-8")


def endpoint_version(request):
    if request.method != "GET":
        return "Method must be GET.", 405
    return dumps({"version": VERSION}).decode("utf-8"), 200


def endpoint_today(request):
    if request.method != "GET":
        return "Method must be GET.", 405
    code = request.args.get("code")
    if not code:
        return "Code is required.", 400
    # fetch data
    data = ezneis.get_school(KEY, code)
    date = datetime.today().strftime("%Y%m%d")
    data.load_meals(date=date)
    return to_json(data.meals), 200


def endpoint_auto(request):
    if request.method != "GET":
        return "Method must be GET.", 405
    code = request.args.get("code")
    if not code:
        return "Code is required.", 400
    # fetch data
    data = ezneis.get_school(KEY, code)
    date = datetime.today().strftime("%Y%m%d")
    data.load_meals(date=date)
    meals = data.meals
    today = datetime.today()
    today_sec = today.hour * 3600 + today.minute * 60 + today.second
    match today_sec:
        case s if s < BREAKFASTS: meals = meals.breakfasts
        case s if s < LUNCHES:    meals = meals.lunches
        case s if s < DINNERS:    meals = meals.dinners
        case _:                   return "[]", 200
    return to_json(meals), 200


@functions_framework.http
def endpoint(request):
    path = request.path.strip("/")
    match path:
        case "version": return endpoint_version(request)
        case "today":   return endpoint_today(request)
        case "auto":    return endpoint_auto(request)
        case _:         return "Endpoint Not Found.", 404


@functions_framework.errorhandler(500)
def error_handler(error):
    original = error.original_exception
    if isinstance(original, ezneis.exceptions.DataNotFoundException):
        return "Data Not Found.", 404
    return "Unknown Error.", 500
