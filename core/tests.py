from django.test import TestCase

from django.test import TestCase
from core.templatetags.core_tags import abs_filter

class TemplateTagsTest(TestCase):
    def test_abs_filter(self):
        self.assertEqual(abs_filter(-10), 10)
        self.assertEqual(abs_filter(10), 10)
        self.assertEqual(abs_filter("-5.5"), 5.5)
        self.assertEqual(abs_filter(None), 0)
        self.assertEqual(abs_filter("gecersiz"), "gecersiz")

