from __future__ import absolute_import
import os
from sys import platform


def locate_browser_process():
    names = []

    if os.getenv('WEBFRIEND_BROWSER'):
        names.append(os.getenv('WEBFRIEND_BROWSER').split(':'))

    if platform.startswith('linux'):
        names = [
            'chromium-browser',
            'google-chrome',
        ]

    elif platform == 'darwin':
        names = [
            '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary',
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium',
        ]

    # We'll get there...
    # elif platform == 'win32':
    #     names = []

    if not len(names):
        raise Exception("Unsupported platform '{}'".format(platform))

    for name in names:
        name = which(name)

        if name:
            return name

    raise Exception("Unable to locate browser process")


def which(base):
    if os.path.exists(base):
        return base

    for path in os.environ['PATH'].split(os.pathsep):
        if os.path.exists(os.path.join(path, base)):
            return os.path.join(path, base)

    return None
