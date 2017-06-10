import os.path
import random
import inspect
import importlib
import string

PACKAGE_ROOT = os.path.abspath(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

PACKAGE_NAME = os.path.basename(PACKAGE_ROOT)


def random_string(count, charset=string.lowercase + string.digits):
    return ''.join(random.sample(charset, count))


def autotype(value):
    if isinstance(value, basestring):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            try:
                return int(value)
            except ValueError:
                pass

            try:
                return float(value)
            except ValueError:
                pass

    return value


def get_module_from_string(string, package=None):
    parts = string.split('.')
    remainder = []

    while len(parts):
        try:
            return importlib.import_module('.'.join(parts), package=package), remainder
        except ImportError:
            remainder = [parts.pop()] + remainder

    return None, string.split('.')


def resolve_object(parts, parent=None):
    if not parent:
        parent = globals()

    while len(parts):
        proceed = False

        for member in inspect.getmembers(parent):
            if member[0] == parts[0]:
                parent = member[1]
                parts = parts[1:]
                proceed = True
                break

        if not proceed:
            return None

    return parent
