from __future__ import absolute_import
from unittest import TestCase
from . import execute_script
from . import parser


class ScriptingTest(TestCase):
    def setUp(self):
        self.maxDiff = 10000

    def _eval(self, script):
        return execute_script(None, script).as_dict()

    def test_assignment(self):
        self.assertEqual({
            'null': None,
            'a': 1,
            'b': True,
            'c': u"Test",
            'c1': u"Test Test",
            'c2': u"Test {c}",
            'd': 3.14159,
            'e': [
                1,
                True,
                u"Test",
                3.14159,
                [
                    1,
                    True,
                    u"Test",
                    3.14159,
                ],
                {
                    'ok': True,
                }
            ],
            'f': {
                'ok': True,
            },
            'g': u'g',
            'h': u'h',
            'i': u'i',
            'j': u'j',
            'k': None,
            'l': u'l',
            'm': u'm',
            'o': u'o',
            'p': None,
            'q': u'q',
            's': u's',
            't': True,
            'u': None,
            'v': 1,
            'w': True,
            'x': u"Test",
            'y': 3.14159,
            'z': [1, True, u"Test", 3.14159],
            'aa': 1,
            'bb': True,
            'cc': u"Test",
            'dd': 3.14159,
            'ee': {
                'ok': True,
                'always': {
                    'finishing': {
                        'each_others': u'sentences',
                    },
                },
            },
            'ee1': {
                'finishing': {
                    'each_others': u'sentences',
                },
            },
            'ee2': {
                'each_others': u'sentences',
            },
            'ee3': u'sentences',
            'ee4': None,
        }, self._eval("""
            # set variables of with values of every type
            $null = null
            $a = 1
            $b = true
            $c = "Test"
            $c1 = "Test {c}"
            $c2 = 'Test {c}'
            $d = 3.14159
            $e = [1, true, "Test", 3.14159, [1, true, "Test", 3.14159], {ok:true}]
            $f = {
                ok: true,
            }
            $g, $h, $i = "g", "h", "i"
            $j, $k = "j"
            $l, $m = ["l", "m", "n"]
            $o, $p = ["o"]
            $q, _, $s = ["q", "r", "s"]
            $t = $f.ok
            $u = $f.nonexistent
            $v, $w, $x, $y, $z = [1, true, "Test", 3.14159, [1, true, "Test", 3.14159]]

            # capture command results as variables, and also put a bunch of them on the same line
            put 1 -> $aa; put true -> $bb; put "Test" -> $cc; put 3.14159 -> $dd
            put {
                ok: true,
                always: {
                    finishing: {
                        each_others: "sentences",
                    },
                },
            } -> $ee

            $ee1, $ee2 = $ee.always, $ee.always.finishing
            $ee3, $ee4 = [$ee.always.finishing.each_others, $ee.always.finishing.each_others.sandwiches]
        """))

    def test_if_scopes(self):
        self.assertEqual({
            'a':             u'top_a',
            'b':             u'top_b',
            'a_if':          u'top_a',
            'b_if':          u'if_b',
            'a_if_if':       u'if_if_a',
            'b_if_if':       u'if_b',
            'a_after_if_if': u'top_a',
            'b_after_if_if': u'if_b',
            'a_after_if':    u'top_a',
            'b_after_if':    u'top_b',
            'enter_if_val':  51,
            'enter_el_val':  61,
            'result':        None,
        }, self._eval("""
            $a             = "top_a"
            $b             = "top_b"
            $a_if          = null
            $b_if          = null
            $a_if_if       = null
            $b_if_if       = null
            $a_after_if_if = null
            $b_after_if_if = null
            $a_after_if    = null
            $b_after_if    = null

            if $b = "if_b"; $b {
                $a_if = $a
                $b_if = $b

                if $a = "if_if_a"; $a {
                    $a_if_if = $a
                    $b_if_if = $b
                }

                $a_after_if_if = $a
                $b_after_if_if = $b
            }

            $a_after_if = $a
            $b_after_if = $b
            $enter_if_val = null
            $enter_el_val = null

            # if condition trigger, verify condition value, populate via assignment
            if $value = 51; $value > 50 {
                $enter_if_val = 51
            } else {
                $enter_if_val = 9999
            }

            # else condition trigger, verify condition value, populate via command output
            if put 61 -> $value; $value > 100 {
                $enter_el_val = 7777
            } else {
                $enter_el_val = 61
            }

            $result = null
        """))

    def test_syntax_errors(self):
        with self.assertRaises(parser.exceptions.ScriptError):
            self._eval("nonexistent")

    def test_loops_all_sorts_of_loops(self):
        self.assertEqual({
            'forevers':        9,
            'double_break':    [4, 1],
            'double_continue': [8, 9],
            'iterations':      4
        }, self._eval("""
            $forevers = 0
            $double_break = null
            $double_continue = null
            $iterations = null
            $things = [1,2,3,4,5]

            loop {
                if not $index < 10 {
                    break
                }

                $forevers = $index
            }

            loop $x in $things {
                $iterations = $index
            }

            loop count 10 {
                $topindex = $index

                loop count 10 {
                    if $topindex == 4 {
                        if $index == 2 {
                            break 2
                        }
                    }

                    $double_break = [$topindex, $index]
                }
            }

            loop count 10 {
                $topindex = $index

                loop count 10 {
                    if $topindex == 9 {
                        if $index >= 0 {
                            continue 2
                        }
                    }

                    $double_continue = [$topindex, $index]
                }
            }

            unset $things
        """))
