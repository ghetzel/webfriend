#!/usr/bin/env python
import logging
from webfriend.browser import Chrome
from webfriend.scripting.environment import Environment

logging.basicConfig(level=logging.DEBUG)

with Chrome() as browser:
    commands = Environment(browser=browser)

    # navigate to Hacker News
    www = commands.core.go('https://nytimes.com')

    # log the result of loading the page
    logging.info("Page loaded in {www[timing][requestTime]}ns".format(www=www))
    logging.info("URL {www[url]}: Loaded with HTTP {www[status]}".format(www=www))

    # take a screenshot of the current page
    commands.page.screenshot('hackernews.png')

    # and, while we're at it, retrieve all the cookies that we have, too
    for index, cookie in enumerate(commands.cookies.all()):
        logging.info("[{index}] {cookie[name]}:".format(
            index=index,
            cookie=cookie
        ))

        for k, v in cookie.items():
            logging.info("  {k:13s} {v}".format(k=k, v=v))
