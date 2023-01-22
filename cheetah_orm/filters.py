"""Cheetah ORM - Filters"""

import inspect

from .common import Field


# Functions
# =========
def _fields(obj):
    return inspect.isdatadescriptor(obj)
