import unittest
from unittest import TestCase
from unittest.mock import patch

from bank2ynab.ynab_api import YNAB_API


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

    @unittest.skip("Not tested yet.")
    def test_api_read(self):
        raise NotImplementedError

    @patch.object(YNAB_API, "select_account")
    def test_process_transactions(self, mock_account_selection):
        mock_account_selection.return_value = "budget id", "account id"
        tests = [
            {"test": {}, "expected": {}},
            {"test": {}, "expected": {}},
        ]
        for test in tests:
            with self.subTest(
                "Test different transaction dictionaries.", test=test
            ):
                test_dict = test["test"]
                test_api_obj = YNAB_API()
                test_output = test_api_obj.process_transactions(
                    transaction_data=test_dict
                )
                self.assertDictEqual(test_dict["expected"], test_output)

    @unittest.skip("Not tested yet.")
    def test_post_transactions(self):
        raise NotImplementedError

    @unittest.skip("Not tested yet.")
    def test_list_transactions(self):
        raise NotImplementedError

    @unittest.skip("Not tested yet.")
    def test_list_accounts(self):
        raise NotImplementedError

    @unittest.skip("Not tested yet.")
    def test_list_budgets(self):
        raise NotImplementedError

    # @patch("ynab_api.option_selection")
    # @patch.object(YNAB_API, "list_accounts")
    # def test_select_account(self, mock_list_acs, mock_option_sel):
    #     """
    #     Test account selection logic
    #     """
    #     test_class = YNAB_API(self.cp)
    #     test_banks = [
    #         ("test_api_existing_bank", "Test Budget ID 1",
    # "Test Account ID"),
    #         ("test_api_existing_bank_2", "Test Budget ID 2", "ID #2"),
    #     ]
    #     test_class.config_path = self.TEMPCONFPATH
    #     test_class.config_handler = configparser.RawConfigParser()
    #     test_class.config_handler.read(test_class.config_path)

    #     mock_ids = [
    #         ("Account 1", "Test Budget ID 1", "ID #1"),
    #         ("Account 2", "Test Budget ID 2", "ID #2"),
    #         ("Account 3", "Test Budget ID 1", "ID #3"),
    #     ]
    #     mock_list_acs.return_value = mock_ids
    #     mock_option_sel.side_effect = ["Test Budget ID 2", "ID #2"]

    #     for bank, budget_id, ac_id in test_banks:
    #         with self.subTest("Test account selection."):
    #             b_id, a_id = test_class.select_account(bank)
    #             self.assertEqual(b_id, budget_id)
    #             self.assertEqual(a_id, ac_id)

    @unittest.skip("Not tested yet.")
    def test_save_account_selection(self):
        raise NotImplementedError

    @unittest.skip("Not tested yet.")
    def test_option_selection(self):
        raise NotImplementedError

    @unittest.skip("Unsure how to test this in a way that makes sense.")
    def test_int_input(self):

        raise NotImplementedError


#     @unittest.skip("Test not implemented yet")
#     def test_create_transaction(self):
#         test_class = YNAB_API(self.cp)
#         test_transactions = [
#             (
#                 ["2019-01-01", "Mimsy", "Category", "Memo", 400, 0],
#                 {
#                     "account_id": "account_id",
#                     "date": "2019-01-01",
#                     "payee_name": "Mimsy",
#                     "amount": -400000,
#                     "memo": "Memo",
#                     "category": "Category",
#                     "cleared": "cleared",
#                     "import_id": "YNAB:-400000:2019-01-01:1",
#                     "payee_id": None,
#                     "category_id": None,
#                     "approved": False,
#                     "flag_color": None,
#                 },
#             ),
#             (
#                 ["2019-01-01", "Mimsy", "Category", "Memo", 400, ""],
#                 {
#                     "account_id": "account_id",
#                     "date": "2019-01-01",
#                     "payee_name": "Mimsy",
#                     "amount": -400000,
#                     "memo": "Memo",
#                     "category": "Category",
#                     "cleared": "cleared",
#                     "import_id": "YNAB:-400000:2019-01-01:2",
#                     "payee_id": None,
#                     "category_id": None,
#                     "approved": False,
#                     "flag_color": None,
#                 },
#             ),
#             (
#                 ["2019-01-01", "Mimsy", "Category", "Memo", "", 500],
#                 {
#                     "account_id": "account_id",
#                     "date": "2019-01-01",
#                     "payee_name": "Mimsy",
#                     "amount": 500000,
#                     "memo": "Memo",
#                     "category": "Category",
#                     "cleared": "cleared",
#                     "import_id": "YNAB:500000:2019-01-01:1",
#                     "payee_id": None,
#                     "category_id": None,
#                     "approved": False,
#                     "flag_color": None,
#                 },
#             ),
#             (
#                 ["2019-01-01", "Borogrove", "Category", "Memo", 600, ""],
#                 {
#                     "account_id": "account_id",
#                     "date": "2019-01-01",
#                     "payee_name": "Borogrove",
#                     "amount": -600000,
#                     "memo": "Memo",
#                     "category": "Category",
#                     "cleared": "cleared",
#                     "import_id": "YNAB:-600000:2019-01-01:1",
#                     "payee_id": None,
#                     "category_id": None,
#                     "approved": False,
#                     "flag_color": None,
#                 },
#             ),
#         ]

#         transactions = []
#         for test_row, target_transaction in test_transactions:
#             test_transaction = test_class.create_transaction(
#                 "account_id", test_row, transactions
#             )
#             transactions.append(test_transaction)

#             for key in test_transaction:
#                 self.assertEqual(
#                     target_transaction[key], test_transaction[key]
#                 )

#     @unittest.skip("Test not implemented yet")
#     def test_create_import_id(self):
#         test_class = YNAB_API(self.cp)

#         test_values = [
#             (100, "2019-01-01", "YNAB:100:2019-01-01:1"),  # no duplicate
#             (200, "2019-01-01", "YNAB:200:2019-01-01:2"),  # 1 duplicate
#             (300, "2019-01-01", "YNAB:300:2019-01-01:3"),  # 2 duplicates
#             (400, "2019-01-01", "YNAB:400:2019-01-01:1"),  # no duplicate
#             (500, "2019-01-01", "YNAB:500:2019-01-01:1"),  # no duplicate
#             (600, "2019-01-01", "YNAB:600:2019-01-01:2"),  # 1 duplicate
#         ]

#         test_transactions = [
#             {
#                 "account_id": "Account",
#                 "date": "2019-01-01",
#                 "payee_name": "Person",
#                 "amount": 200,
#                 "memo": "Memo",
#                 "category": "Category",
#                 "cleared": "cleared",
#                 "import_id": "YNAB:200:2019-01-01:1",
#                 "payee_id": None,
#                 "category_id": None,
#                 "approved": False,
#                 "flag_color": None,
#             },
#             {
#                 "account_id": "Account",
#                 "date": "2019-01-01",
#                 "payee_name": "Person",
#                 "amount": 300,
#                 "memo": "Memo",
#                 "category": "Category",
#                 "cleared": "cleared",
#                 "import_id": "YNAB:300:2019-01-01:1",
#                 "payee_id": None,
#                 "category_id": None,
#                 "approved": False,
#                 "flag_color": None,
#             },
#             {
#                 "account_id": "Account",
#                 "date": "2019-01-01",
#                 "payee_name": "Person",
#                 "amount": 300,
#                 "memo": "Memo",
#                 "category": "Category",
#                 "cleared": "cleared",
#                 "import_id": "YNAB:300:2019-01-01:2",
#                 "payee_id": None,
#                 "category_id": None,
#                 "approved": False,
#                 "flag_color": None,
#             },
#             {
#                 "account_id": "Account",
#                 "date": "2019-01-01",
#                 "payee_name": "Person",
#                 "amount": 600,
#                 "memo": "Memo",
#                 "category": "Category",
#                 "cleared": "cleared",
#                 "import_id": "YNAB:600:2019-01-01:1",
#                 "payee_id": None,
#                 "category_id": None,
#                 "approved": False,
#                 "flag_color": None,
#             },
#         ]

#         for amount, date, target_id in test_values:
#             id = test_class.create_import_id(amount, date, test_transactions)
#             self.assertEqual(id, target_id)


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
