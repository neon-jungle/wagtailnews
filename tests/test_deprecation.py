import json
import warnings

from django.test import TestCase

from wagtailnews.deprecation import DeprecatedCallableStr


class TestDeprecatedCallableStr(TestCase):
    def test_strness(self):
        s = DeprecatedCallableStr('foo', warning='nope', warning_cls=DeprecationWarning)
        self.assertEqual(s, 'foo')
        self.assertEqual(s + 'bar', 'foobar')
        self.assertEqual('bar' + s, 'barfoo')
        self.assertEqual(hash(s), hash('foo'))
        self.assertEqual(json.dumps(s), '"foo"')
        self.assertTrue(isinstance(s, str))

    def test_deprecation(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')

            # Creating one should not trigger a deprecation warning
            s = DeprecatedCallableStr('foo', warning='nope', warning_cls=DeprecationWarning)
            self.assertEqual(len(w), 0)

            # Doing stringy things should not trigger the warning
            out = s + 'bar'
            self.assertEqual(out, 'foobar')
            self.assertEqual(len(w), 0)

            # Calling the string should trigger the warning
            out = s()
            self.assertEqual(out, 'foo')
            self.assertEqual(len(w), 1)
            self.assertEqual(w[0].category, DeprecationWarning)
