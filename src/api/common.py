import os

__all__ = [
    "NAME",
    "KEY"
]


NAME = os.environ.get("TARGET")
KEY = os.environ.get("API_KEY")
if not KEY or not NAME:
    raise EnvironmentError("API_KEY or TARGET is not set.")