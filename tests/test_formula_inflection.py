from unittest import TestCase

from boltons.strutils import pluralize, singularize


class TestFormulaInflection(TestCase):
    def test_singularize_both_plurals(self):
        for plural in ('formulas', 'formulae'):
            for case in (str.lower, str.title, str.upper):
                word = case(plural)
                with self.subTest(word=word):
                    self.assertEqual(singularize(word), case('formula'))

    def test_preserve_preferred_plural(self):
        for case in (str.lower, str.title, str.upper):
            word = case('formula')
            with self.subTest(word=word):
                self.assertEqual(pluralize(word), case('formulas'))

    def test_preserve_existing_plurals(self):
        for plural in ('formulas', 'formulae'):
            for case in (str.lower, str.title, str.upper):
                word = case(plural)
                with self.subTest(word=word):
                    self.assertEqual(pluralize(word), word)
