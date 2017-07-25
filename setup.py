from __future__ import absolute_import
from setuptools import setup, find_packages
from webfriend.info import version

setup(
    name='webfriend',
    description='An API binding and automation control language for the Chrome Remote Debugging API',
    version=version,
    author='Gary Hetzel',
    author_email='garyhetzel@gmail.com',
    url='https://github.com/ghetzel/webfriend',
    install_requires=[
        'click',
        'click-log',
        'colorlog',
        'ephemeral_port_reserve',
        'prompt_toolkit',
        'pygments',
        'requests',
        'termcolor',
        'textx',
        'urlnorm',
        'websocket-client',
    ],
    packages=find_packages(exclude=['*.tests']),
    entry_points={
        'console_scripts': [
            'webfriend = webfriend.cli:main',
        ],
    },
    classifiers=[],
)
