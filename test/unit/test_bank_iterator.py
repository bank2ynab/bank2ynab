from unittest import TestCase


class TestBankIterator(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()


"""def test_build_bank(self):
        b2yb = build_bank(self.defaults)
        self.assertIsInstance(b2yb, B2YBank)
        nullconfig = fix_conf_params(self.cp, "test_plugin")
        nullb = build_bank(nullconfig)
        self.assertIsInstance(nullb, NullBank)
        missingconf = fix_conf_params(self.cp, "test_plugin_missing")
        self.assertRaises(ImportError, build_bank, missingconf)"""
