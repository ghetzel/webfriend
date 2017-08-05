# WebFriend
[![PyPI version](https://badge.fury.io/py/webfriend.svg)](https://badge.fury.io/py/webfriend)


Your friendly friend in modern web automation and testing.

## Overview

Webfriend is a Python library and command-line utility that integrates with the [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/) to control a Google Chrome or Chromium browser instance.  There is also a purpose-built scripting language (called [Friendscript](docs/intro.md)) that is designed to be an easy-to-learn alternative to Python for writing simple or complex browser automation scripts.


Some of the things that you can use Webfriend for:

* Take full-page screenshots of web pages.

* Automate tedious or repetitive tasks on web pages that otherwise would require extensive user input with a keyboard, mouse, or touchscreen device.

* Automatically login to websites with complex authentication flows.

* Extract (i.e. _scrape_) information from web pages and present it in a structured way that other languages and scripts can use as input.


Webfriend by default operates using [Headless Chrome](https://developers.google.com/web/updates/2017/04/headless-chrome) mode, but can also just as easily run Chrome in the foreground in a graphical environment.  Most importantly, however, headless operation allows you to **run Webfriend on servers without running `Xfvb` or `X11`.**  In this sense, it operates as a potentially-faster alternative to _phantomjs_ or _Selenium_ while also providing almost all of the capabilities of the complete Google Chrome/Chromium browser.

## Installation

```
git clone https://github.com/ghetzel/webfriend.git
cd webfriend

# Three Options:

# 1. user-level package install
python setup.py install --user

# 2. system-level package install
python setup.py install

# 3. local environment, invoke with `./env/bin/webfriend`
make
```

## Documentation

* Friendscript (Web Automation Scripting Language)

    - [Beginner's Guide](docs/intro.md)

    - [Language Overview](docs/language.md)

    - [Command Reference](docs/commands.md)
