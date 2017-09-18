# flake8: noqa
from __future__ import absolute_import
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *


class FriendscriptLexer(RegexLexer):
    name = 'Friendscript'
    aliases = ['friendscript']
    filenames = ['*.fs']

    tokens = {
        'root': [
            (r'^#!.*\n', Comment.Hashbang),
            (r'#.*\n', Comment.Single),
            (r'\/.*\/[a-z]*', String.Regex),
            (r'\s+(=~|%|~|!~|<<|->|!=|(?:&|\||\^|\+|-|\*|\/|=|<|>)=?)\s+', bygroups(Operator)),
            (r'\s+(in|is|not)\s+', bygroups(Operator.Word)),
            (r'\s+(as|break|case|continue|else|if|loop(\s+count)?|on|unset|when)\s+', bygroups(Keyword)),
            (r'\d', Number),
            (r'(true|false|null)', Keyword.Pseudo),
            (r'\'', String.Single, 'str'),
            (r'"', String.Double, 'str-double'),
            (r'\$[^\d\W][\w\.]*\b', Name.Variable),
            (r'[\{\},\.\[\];]', Punctuation),
            (r'([\w\d]+)\s*(:)(?!:)', bygroups(Name.Attribute, Punctuation)),
            (r'([\w\d][\w\d]*)(::[\w\d][\w\d]*)*', Name.Function),
            (r'\s+', Text),
        ],
        'str': [
            (r'[^\']', String.Single),
            (r'\'', String.Single, '#pop'),
        ],
        'str-double': [
            (r'{[^}]*}', String.Interpol),
            (r'[^"]', String.Double),
            (r'"', String.Double, '#pop'),
        ],
    }
