from __future__ import absolute_import
from __future__ import unicode_literals
from unittest import TestCase
from webfriend.scripting import parser
from webfriend.scripting.execute import execute_script


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
            'c': "Test",
            'c1': "Test Test",
            'c2': "Test {c}",
            'd': 3.14159,
            'e': [
                1,
                True,
                "Test",
                3.14159,
                [
                    1,
                    True,
                    "Test",
                    3.14159,
                ],
                {
                    'ok': True,
                }
            ],
            'f': {
                'ok': True,
            },
            'g': 'g',
            'h': 'h',
            'i': 'i',
            'j': 'j',
            'k': None,
            'l': 'l',
            'm': 'm',
            'o': 'o',
            'p': None,
            'q': 'q',
            's': 's',
            't': True,
            'u': None,
            'v': 1,
            'w': True,
            'x': "Test",
            'y': 3.14159,
            'z': [1, True, "Test", 3.14159],
            'z0': 1,
            'z1': True,
            'z2': 'Test',
            'z3': 3.14159,
            'aa': 1,
            'bb': True,
            'cc': "Test",
            'dd': 3.14159,
            'ee': {
                'ok': True,
                'always': {
                    'finishing': {
                        'each_others': 'sentences',
                    },
                },
            },
            'ee1': {
                'finishing': {
                    'each_others': 'sentences',
                },
            },
            'ee2': {
                'each_others': 'sentences',
            },
            'ee3': 'sentences',
            'ee4': None,
            'ee5': True,
            'ee6': 'sentences',
            'ekey': 'always',
            'ee7': 'sentences',
            'ee8': {
                'ok': True,
                'always': {
                    'finishing': {
                        'each_others': 'sandwiches',
                        'other': {
                            'stuff': {
                                'too': True,
                            },
                        },
                    },
                },
            },
            'put_1': 'test 1',
            'put_2': 'test {a}',
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

            $z0 = $z[0]
            $z1 = $z[1]
            $z2 = $z[2]
            $z3 = $z[3]

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

            $ee5 = $ee['ok']
            $ee6 = $ee['always'].finishing['each_others']
            $ekey = 'always'
            $ee7 = $ee[$ekey].finishing['each_others']
            $ee8 = $ee
            $ee8.always['finishing'].each_others = 'sandwiches'
            $ee8.always['finishing'].other['stuff'].too = True

            put "test {a}" -> $put_1
            put 'test {a}' -> $put_2
        """))

    def test_if_scopes(self):
        self.assertEqual({
            'a':             'top_a',
            'b':             'top_b',
            'a_if':          'top_a',
            'b_if':          'if_b',
            'a_if_if':       'if_if_a',
            'b_if_if':       'if_b',
            'a_after_if_if': 'top_a',
            'b_after_if_if': 'if_b',
            'a_after_if':    'top_a',
            'b_after_if':    'top_b',
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

    def test_conditionals(self):
        self.assertEqual({
            'ten':            10,
            'unset':          None,
            'true':           True,
            'false':          False,
            'string':         "string",
            'names':          ["Bob", "Steve", "Fred"],
            'if_eq':          True,
            'if_ne':          True,
            'if_eq_null':     True,
            'if_true':        True,
            'if_gt':          True,
            'if_gte':         True,
            'if_lt':          True,
            'if_lte':         True,
            'if_in':          True,
            'if_not_in':      True,
            'if_match_1':     True,
            'if_match_2':     True,
            'if_match_3':     True,
            'if_not_match_1': True,
            'if_not_match_2': True,
            'if_not_match_3': True,
            'if_match_4':     True,
            'if_match_5':     True,
            'if_match_6':     True,
            'if_not_match_4': True,
            'if_not_match_5': True,
            'if_not_match_6': True,
        }, self._eval("""
            $ten = 10
            $unset = null
            $true = true
            $false = false
            $string = "string"
            $names = ["Bob", "Steve", "Fred"]
            $if_eq = null
            $if_ne = null
            $if_eq_null = null
            $if_true = null
            $if_gt = null
            $if_gte = null
            $if_lt = null
            $if_lte = null
            $if_in = null
            $if_not_in = null
            $if_match_1 = null
            $if_match_2 = null
            $if_match_3 = null
            $if_match_4 = null
            $if_match_5 = null
            $if_match_6 = null
            $if_not_match_1 = null
            $if_not_match_2 = null
            $if_not_match_3 = null
            $if_not_match_4 = null
            $if_not_match_5 = null
            $if_not_match_6 = null

            if $ten == 10                    { $if_eq          = true }
            if $unset == null                { $if_eq_null     = true }
            if $ten != 5                     { $if_ne          = true }
            if $ten > 5                      { $if_gt          = true }
            if $ten >= 10                    { $if_gte         = true }
            if $ten < 20                     { $if_lt          = true }
            if $ten <= 10                    { $if_lte         = true }
            if $true                         { $if_true        = true }
            if not $false                    { $if_false       = true }
            if "Steve" in $names             { $if_in          = true }
            if "Bill" not in $names          { $if_not_in      = true }
            if $string =~ /str[aeiou]ng/     { $if_match_1     = true }
            if $string =~ /String/i          { $if_match_2     = true }
            if $string =~ /.*/               { $if_match_3     = true }
            if $string !~ /strong/i          { $if_not_match_1 = true }
            if $string !~ /String/           { $if_not_match_2 = true }
            if $string !~ /^ring$/           { $if_not_match_3 = true }
            if not $string !~ /str[aeiou]ng/ { $if_match_4     = true }
            if not $string !~ /String/i      { $if_match_5     = true }
            if not $string !~ /.*/           { $if_match_6     = true }
            if not $string =~ /strong/i      { $if_not_match_4 = true }
            if not $string =~ /String/       { $if_not_match_5 = true }
            if not $string =~ /^ring$/       { $if_not_match_6 = true }
        """))

    def test_expressions(self):
        self.assertEqual({
            'a': 2,
            'b': 6,
            'c': 20,
            'd': 5,
            'aa': 2,
            'bb': 6,
            'cc': 20,
            'dd': 5,
            # 'f': u'This 2 is {b} and done',
            'put_a': '    this is some stuff',
            'put_b': '    buncha\n    muncha\n    cruncha\n    lines',
        }, self._eval("""
            $a = 1 + 1
            $b = 9 - 3
            $c = 5 * 4
            $d = 50 / 10
            # $e = 4 * -6 * (3 * 7 + 5) + 2 * 7

            $aa = 1
            $aa += 1

            $bb = 9
            $bb -= 3

            $cc = 5
            $cc *= 4

            $dd = 50
            $dd /= 10

            # $f = "This {a}" + ' is {b}' + " and done"

            put begin
                this is some stuff
            end -> $put_a

            put begin
                buncha
                muncha
                cruncha
                lines
            end -> $put_b
        """))

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
