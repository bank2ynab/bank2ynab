from unittest import TestCase

from os.path import join

from bank2ynab import fix_conf_params
from plugins.JLP_Card_UK import JLP_Card_UKPlugin
from test.utils import get_test_confparser

_PY2 = False


class TestJLP_Card_UKPlugin(TestCase):

    def setUp(self):
        global _PY2
        self.cp, self.py2, = get_test_confparser()
        self.defaults = dict(self.cp.defaults())
        self.b = None

    def tearDown(self):
        pass

    def test_read_data(self):
        """ Test that the right number of rows are read from the test files """
        # if you need more tests, add sections to test.conf & specify them here
        (section_name, num_records, fpath) = (
            "test_jlp_card",
            11,
            "MS_JANE_SMITH_01-12-2019_14-12-2019.csv",
        )

        config = fix_conf_params(self.cp, section_name)
        b = JLP_Card_UKPlugin(config, self.py2)
        records = b.read_data(join("test-data", fpath))
        self.assertEqual(len(records), num_records)
        self.assertEqual(records[10][5], "1100.00")
        self.assertEqual(records[4][4], "80.99")
