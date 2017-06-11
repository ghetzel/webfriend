from __future__ import absolute_import
from __future__ import unicode_literals
from unittest import TestCase
from webfriend.scripting.scope import Scope


class ScopeTest(TestCase):
    def test_inheritance_and_overrides(self):
        top = Scope({
            'a': 1,
        })

        one_deep = Scope({
            'b': 2,
        }, parent=top)

        two_deep = Scope({
            'c': 3,
        }, parent=one_deep)

        # ensure that all values are as we expect them from various perspectives
        self.assertEqual(1, top['a'])
        self.assertTrue(top.is_local('a'))

        self.assertEqual(1, one_deep['a'])
        self.assertEqual(2, one_deep['b'])

        self.assertFalse(one_deep.is_local('a'))
        self.assertTrue(one_deep.is_local('b'))

        self.assertEqual(1, two_deep['a'])
        self.assertEqual(2, two_deep['b'])
        self.assertEqual(3, two_deep['c'])

        self.assertFalse(two_deep.is_local('a'))
        self.assertFalse(two_deep.is_local('b'))
        self.assertTrue(two_deep.is_local('c'))

        # ensure that setting a value on a child scope appropriately routes the set to the
        # correct owning scope, and that all children immediately see the update
        two_deep['a'] = 11
        self.assertFalse(two_deep.is_local('a'))
        self.assertEqual(11, two_deep['a'])

        self.assertFalse(one_deep.is_local('a'))
        self.assertEqual(11, one_deep['a'])

        self.assertTrue(top.is_local('a'))
        self.assertEqual(11, top['a'])

        # ensure that force-setting a value creates that value on the scope it was set on,
        # regardless of parent membership
        two_deep.set('b', 22, force=True)
        self.assertTrue(two_deep.is_local('b'))
        self.assertEqual(22, two_deep['b'])

        # make sure it's still the old value from the parent's perspective
        self.assertTrue(one_deep.is_local('b'))
        self.assertEqual(2, one_deep['b'])

        # and that top can't see it at all
        self.assertFalse(top.is_local('b'))
        self.assertIsNone(top.get('b'))

    def test_nested_inheritance_and_overrides(self):
        top = Scope({
            'a': {
                'thing': 1,
            },
        })

        one_deep = Scope({
            'b': {
                'thing': 2,
            },
        }, parent=top)

        two_deep = Scope({
            'c': {
                'thing': 3,
            },
        }, parent=one_deep)

        # ensure that all values are as we expect them from various perspectives
        self.assertEqual(1, top['a.thing'])
        self.assertTrue(top.is_local('a.thing'))

        self.assertEqual(1, one_deep['a.thing'])
        self.assertEqual(2, one_deep['b.thing'])

        self.assertFalse(one_deep.is_local('a.thing'))
        self.assertTrue(one_deep.is_local('b.thing'))

        self.assertEqual(1, two_deep['a.thing'])
        self.assertEqual(2, two_deep['b.thing'])
        self.assertEqual(3, two_deep['c.thing'])

        self.assertFalse(two_deep.is_local('a.thing'))
        self.assertFalse(two_deep.is_local('b.thing'))
        self.assertTrue(two_deep.is_local('c.thing'))

        # ensure that setting a value on a child scope appropriately routes the set to the
        # correct owning scope, and that all children immediately see the update
        two_deep['a.thing'] = 11
        self.assertFalse(two_deep.is_local('a.thing'))
        self.assertEqual(11, two_deep['a.thing'])

        self.assertFalse(one_deep.is_local('a.thing'))
        self.assertEqual(11, one_deep['a.thing'])

        self.assertTrue(top.is_local('a.thing'))
        self.assertEqual(11, top['a.thing'])

        # ensure that force-setting a value creates that value on the scope it was set on,
        # regardless of parent membership
        two_deep.set('b.thing', 22, force=True)
        self.assertTrue(two_deep.is_local('b.thing'))
        self.assertEqual(22, two_deep['b.thing'])

        # make sure it's still the old value from the parent's perspective
        self.assertTrue(one_deep.is_local('b.thing'))
        self.assertEqual(2, one_deep['b.thing'])

        # and that top can't see it at all
        self.assertFalse(top.is_local('b.thing'))
        self.assertIsNone(top.get('b.thing'))

        # I'll just leave this one here...
        a = one_deep

        # assert that this remains true
        a['g.thing'] = None
        self.assertIsNone(a['g.thing'])

        # ensure that creating a value on one_deep is visible but not local to two_deep, and
        # not visible from top
        one_deep['z.y.x'] = 42
        self.assertTrue(one_deep.is_local('z'))
        self.assertTrue(one_deep.is_local('z.y'))
        self.assertTrue(one_deep.is_local('z.y.x'))
        self.assertEqual(42, one_deep['z.y.x'])

        self.assertFalse(two_deep.is_local('z'))
        self.assertFalse(two_deep.is_local('z.y'))
        self.assertFalse(two_deep.is_local('z.y.x'))
        self.assertEqual(42, two_deep['z.y.x'])

    def test_scope_nested_retrieval(self):
        scope = Scope({
            'top': True,
            'nested': {
                'values': {
                    'are': [
                        'fun',
                    ]
                }
            }
        })

        self.assertEqual(True, scope.get('top'))

        self.assertEqual({
            'values': {
                'are': ['fun'],
            }
        }, scope.get('nested'))

        self.assertEqual({
            'are': ['fun'],
        }, scope.get('nested.values'))

        self.assertEqual(['fun'], scope.get('nested.values.are'))

        self.assertIsNone(scope.get('nested.nonexistent'))

        self.assertIsNone(scope.get('nested.values.nonexistent'))

        self.assertIsNone(scope.get('nested.double.nonexistent'))

        self.assertTrue('top' in scope)
        self.assertTrue('nested' in scope)
        self.assertTrue('nested.values' in scope)
        self.assertTrue('nested.values.are' in scope)
        self.assertFalse('nested.values.nonexistent' in scope)
        self.assertFalse('nested.nonexistent.are' in scope)
        self.assertFalse('nested.double.nonexistent' in scope)

        scope.unset('nested.values')
        self.assertFalse('nested.values.are' in scope)
        self.assertFalse('nested.values' in scope)
        self.assertTrue('nested' in scope)
