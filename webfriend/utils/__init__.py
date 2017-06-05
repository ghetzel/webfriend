import os.path
import random
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
