import unittest
from unittest import TestCase

from bank2ynab.ynab_api import apply_mapping, generate_name_id_list


class TestYNAB_API(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    @unittest.skip("Not tested yet.")
    def test_init(self):
        raise NotImplementedError

    @unittest.skip("Not tested yet.")
    def test_run(self):
        raise NotImplementedError

    def test_apply_mapping(self):
        test_data = {
            "bank 1": [
                {"test field 1": 1},
                {"test field 2": 1},
                {"test field 3": 1},
            ],
            "bank 2": [
                {"test field 1": 2},
                {"test field 2": 2},
                {"test field 3": 2},
            ],
            "bank 3": [
                {"test field 1": 3},
                {"test field 2": 3},
                {"test field 3": 3},
            ],
        }
        test_mapping = {
            "bank 1": {"budget_id": "budget 1", "account_id": "account_1"},
            "bank 2": {"budget_id": "budget 1", "account_id": "account_2"},
            "bank 3": {"budget_id": "budget 3", "account_id": "account_4"},
        }

        expected_output = {
            "budget 1": {
                "transactions": [
                    {"test field 1": 1, "account_id": "account_1"},
                    {"test field 2": 1, "account_id": "account_1"},
                    {"test field 3": 1, "account_id": "account_1"},
                    {"test field 1": 2, "account_id": "account_2"},
                    {"test field 2": 2, "account_id": "account_2"},
                    {"test field 3": 2, "account_id": "account_2"},
                ]
            },
            "budget 3": {
                "transactions": [
                    {"test field 1": 3, "account_id": "account_4"},
                    {"test field 2": 3, "account_id": "account_4"},
                    {"test field 3": 3, "account_id": "account_4"},
                ]
            },
        }

        test_dict = apply_mapping(test_data, test_mapping)

        self.assertDictEqual(expected_output, test_dict)

    def test_generate_name_id_list(self):
        test_dict = {
            "id1": {"name": "name1", "field": "etc1"},
            "id2": {"name": "name2", "field": "etc2"},
            "id3": {"name": "name3", "field": "etc3"},
            "id4": {"name": "name4", "field": "etc4"},
        }
        expected_output = [
            ["name1", "id1"],
            ["name2", "id2"],
            ["name3", "id3"],
            ["name4", "id4"],
        ]
        test_output = generate_name_id_list(test_dict)
        self.assertListEqual(expected_output, test_output)

    @unittest.skip("Not tested yet.")
    def test_save_account_selection(self):
        raise NotImplementedError


#     @unittest.skip("Test not implemented yet")
#     def test_save_account_selection(self):
#         """
#         Test that account info is saved under the correct bank and
#         in the correct file.
#         """
#         test_class = YNAB_API(self.cp)
#         test_budget_id = "Test Budget ID"
#         test_account_id = "Test Account ID"
#         test_banks = ["New Bank", "Existing Bank"]
#         test_class.config_path = self.TEMPCONFPATH
#         test_class.config_handler = configparser.RawConfigParser()
#         test_class.config_handler.read(test_class.config_path)

#         # save test bank details to test config
#         for test_bank in test_banks:
#             test_class.save_account_selection(
#                 test_bank, test_budget_id, test_account_id
#             )
#         # check test config for test bank details & make sure ID matches
#         config = configparser.RawConfigParser()
#         config.read(test_class.user_config_path)
#         for test_bank in test_banks:
#             test_id = config.get(test_bank, "YNAB Account ID")
#             self.assertEqual(
#                 test_id, "{}||{}".format(test_budget_id, test_account_id)
#             )
