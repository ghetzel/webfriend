from __future__ import absolute_import
from __future__ import unicode_literals
from unittest import TestCase
from webfriend.scripting.execute import execute_script


class FormatProxyTest(TestCase):
    def setUp(self):
        self.maxDiff = 10000

    def _eval(self, script):
        return execute_script(None, script).as_dict()

    def test_autotype(self):
        self.assertEqual({
            'a': 42,
            'b': 3.1415,
            'c': True,
            'd': True,
            'e': True,
            'f': False,
            'g': False,
            'h': False,
            'i': -42,
            'j': -3.1415,
            'k': 0,
            'l': 1,
        }, self._eval("""
            fmt::autotype "42" -> $a
            fmt::autotype "3.1415" -> $b
            fmt::autotype "true" -> $c
            fmt::autotype "True" -> $d
            fmt::autotype "TRUE" -> $e
            fmt::autotype "false" -> $f
            fmt::autotype "False" -> $g
            fmt::autotype "FALSE" -> $h
            fmt::autotype "FALSE" -> $h
            fmt::autotype "-42" -> $i
            fmt::autotype "-3.1415" -> $j
            fmt::autotype "0" -> $k
            fmt::autotype "1" -> $l
        """))

    def test_strip(self):
        self.assertEqual({
            'a': 'Value',
            'b': 'Value',
            'c': 'Value',
            'd': 'Value',
            'e': 'Value',
            'f': 'Value',
            'g': '    Value',
            'h': 'Value    ',
            'i': 'Value!',
            'j': 'Value    ',
            'k': '    Value',
        }, self._eval("""
            fmt::strip 'Value' -> $a
            fmt::strip '    Value' -> $b
            fmt::strip 'Value    ' -> $c
            fmt::strip '  \n\nValue   ' -> $d
            fmt::strip begin

                Value
            end -> $e

            fmt::strip 'Value' {
                characters: '$',
            } -> $f

            fmt::strip '$    Value' {
                characters: '$',
            } -> $g

            fmt::strip 'Value    $$$' {
                characters: '$',
            } -> $h

            fmt::strip '$$#@$Value!$&#' {
                characters: '@#&$',
            } -> $i

            fmt::lstrip '    Value    ' -> $j
            fmt::rstrip '    Value    ' -> $k
        """))
