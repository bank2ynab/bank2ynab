from os.path import join
from unittest import TestCase

from bank2ynab import fix_conf_params
from plugins import swedebank
from test.utils import get_test_confparser


class TestSwedebankPlugin(TestCase):
    def test_read_data(self):
        cp, is_py2 = get_test_confparser()
        sbc = fix_conf_params(cp, "test_plugin_swedebank")
        sb = swedebank.build_bank(sbc, is_py2)
        self.assertIsInstance(sb, swedebank.SwedebankPlugin)
        self.assertEqual("SwedeBank", sb.name)
        data = sb.read_data(join("test-data", "test_swedebank_statement.xls"))
        self.assertEqual(len(data), 13)
        # check date parsing was correct
        self.assertEqual(data[0][0], "01/10/2014")
        # check record correctly set as outflow
        self.assertEqual(data[0][4], "15.31")
        # check record correctly set as inflow
        self.assertEqual(data[-1][5], "2863.63")
