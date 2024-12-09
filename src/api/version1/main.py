from .meals import app as meals
from .timetables import app as timetables
from fastapi import FastAPI

__all__ = [
    "app"
]


app = FastAPI()


app.mount("/meals", meals)
app.mount("/timetables", timetables)


if __name__ == "__main__":
    raise EnvironmentError("This module cannot be run directly.")
