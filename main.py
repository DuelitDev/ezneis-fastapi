import ezneis
import ezneis.exceptions
import functions_framework
from datetime import date, datetime
from dataclasses import asdict, is_dataclass
from enum import Enum
from json import JSONEncoder, dumps
from os import environ

VERSION = "1.0.0"
KEY = environ["API_KEY"]
CORS = environ.get("CORS_DOMAINS", "*")
HEADERS = {"Access-Control-Allow-Origin": CORS}

BREAKFASTS = 8 * 3600 + 10 * 60  # 8:10
LUNCHES = 13 * 3600 + 10 * 60  # 13:10
DINNERS = 18 * 3600 + 10 * 60  # 18:10


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        elif isinstance(o, date):
            return o.strftime("%Y-%m-%d")
        elif isinstance(o, Enum):
            return o.value
        return super().default(o)


def to_json(models):
    temp = [asdict(model) for model in models]
    return dumps(temp, cls=CustomJSONEncoder, ensure_ascii=False)


def endpoint_version():
    return dumps({"version": VERSION}, ensure_ascii=False)


def endpoint_today(code):
    data = ezneis.get_school(KEY, code)
    data.load_meals(date=datetime.today().strftime("%Y%m%d"))
    return to_json(data.meals)


def endpoint_auto(code):
    data = ezneis.get_school(KEY, code)
    data.load_meals(date=datetime.today().strftime("%Y%m%d"))
    meals = data.meals
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
            return "[]"
    return to_json(meals)


@functions_framework.errorhandler(500)
def error_handler(error):
    original = error.original_exception
    if isinstance(original, AssertionError):
        return "Valid Code is Required.", 400, HEADERS
    elif isinstance(original, ezneis.exceptions.DataNotFoundException):
        return "Data Not Found.", 404, HEADERS
    return "Unknown Error.", 500, HEADERS


@functions_framework.http
def endpoint(request):
    if request.method != "GET":
        return "Method must be GET.", 405, HEADERS
    code = request.args.get("code")
    path = request.path.strip("/")
    match path:
        case "version":
            return endpoint_version(), 200, HEADERS
        case "today":
            assert code is not None and len(code) == 7
            return endpoint_today(code), 200, HEADERS
        case "auto":
            assert code is not None and len(code) == 7
            return endpoint_auto(code), 200, HEADERS
        case _:
            return "Endpoint Not Found.", 404, HEADERS
