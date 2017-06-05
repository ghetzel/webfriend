#!/usr/bin/env python
import os
import json
from webfriend import Chrome
from webfriend.scripting import CommandSet, commands
import logging

logging.basicConfig(level=logging.DEBUG)


if os.getenv('DEBUG') == 'true':
    Chrome.browser_arguments.remove('--headless')
    Chrome.browser_arguments = ['--temp-profile'] + Chrome.browser_arguments

with Chrome() as browser:
    commandset = CommandSet(browser=browser)

    commandset.register(commands.CoreProxy)
    commandset.register(commands.PageProxy)
    commandset.ready()

    print(json.dumps(commandset.core.go('https://google.com'), indent=4))
    # print(commandset.page.source())
