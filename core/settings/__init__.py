import os

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

if DEBUG:
    from .development import *
else:
    from .production import *
