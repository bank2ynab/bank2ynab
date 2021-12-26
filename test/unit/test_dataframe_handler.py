from unittest import TestCase

import pandas as pd
from bank2ynab.dataframe_handler import (
    add_missing_columns,
    auto_memo,
    auto_payee,
    cd_flag_process,
    clean_monetary_values,
    fill_api_columns,
    fix_amount,
    fix_date,
    merge_duplicate_columns,
    output_json_transactions,
    remove_invalid_rows,
)


class TestDataframeHandler(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_merge_duplicate_columns(self):
        """Check that merging of duplicate columns works correctly."""
        test_dfs = [
            {
                "data": {
                    "Amount": [4, 3, 2, 1],
                    "Payee": ["four", "three", "two", "one"],
                },
                "input_cols": ["Amount", "Payee"],
                "desired_output": ["Amount", "Payee"],
            },
            {
                "data": {
                    "Amount": [4, 3, 2, 1],
                    "Payee": ["four", "three", "two", "one"],
                    "Memo": ["four", "three", "two", "one"],
                },
                "input_cols": ["Amount", "Payee", "Payee"],
                "desired_output": ["Amount", "Payee", "Payee 0"],
            },
        ]

        for test in test_dfs:
            test_df = merge_duplicate_columns(
                pd.DataFrame(test["data"]), test["input_cols"]
            )

            TestCase.assertCountEqual(
                self, test["desired_output"], list(test_df)
            )

    def test_add_missing_columns(self):
        """Check that adding missing columns works correctly."""
        desired_cols = ["One", "Two", "Three", "Four"]
        test_datasets = [
            {"One": [], "Two": [], "Three": [], "Four": []},
            {"One": [], "Two": [], "Four": []},
            {"One": [], "Two": []},
            {},
        ]
        for dataset in test_datasets:
            test_df = pd.DataFrame(dataset)
            test_df = add_missing_columns(test_df, list(test_df), desired_cols)
            # check if column names contain all desired values
            TestCase.assertCountEqual(self, desired_cols, list(test_df))

    def test_cd_flag_process(self):
        """if len(cd_flags) == 3:
        outflow_flag = cd_flags[2]
        # if this row is indicated to be outflow, make inflow negative
        df.loc[df["CDFlag"] is outflow_flag, ["Inflow"]] = f"-{df['Inflow']}"
        return df"""

        test_data = [
            {
                "data": {"Inflow": [10]},
                "cd_flags": [],
                "target_inflow": 10,
            },
            {
                "data": {"Inflow": [10], "CDFlag": ["Inflow"]},
                "cd_flags": [7, "Inflow", "Outflow"],
                "target_inflow": 10,
            },
            {
                "data": {"Inflow": [10], "CDFlag": ["Outflow"]},
                "cd_flags": [7, "Inflow", "Outflow"],
                "target_inflow": -10,
            },
            {
                "data": {"Inflow": [10], "CDFlag": ["Outflow"]},
                "cd_flags": [7, "Inflow"],
                "target_inflow": 10,
            },
        ]

        for dataset in test_data:
            test_df = pd.DataFrame(dataset["data"])
            test_df = cd_flag_process(test_df, dataset["cd_flags"])
            TestCase.assertEqual(
                self, dataset["target_inflow"], test_df["Inflow"].iloc[0]
            )

    def test_fix_amount(self):
        test_df = fix_amount()
        raise NotImplementedError

    def test_clean_monetary_values(self):
        test_df = clean_monetary_values()
        raise NotImplementedError

    def test_remove_invalid_rows(self):
        test_df = remove_invalid_rows()
        raise NotImplementedError

    def test_auto_memo(self):
        test_df = auto_memo()
        raise NotImplementedError

    def test_auto_payee(self):
        test_df = auto_payee()
        raise NotImplementedError

    def test_fix_date(self):
        test_df["Date"] = fix_date()
        raise NotImplementedError

    def test_fill_api_columns(self):
        test_df = fill_api_columns()
        raise NotImplementedError

    def test_output_json_transactions(self):
        # TODO let's directly reference YNAB API documentation here
        # and compare with the desired output
        test_df = pd.DataFrame(
            {
                "account_id": [1],
                "date": [2],
                "payee_name": [3],
                "amount": [4],
                "memo": [5],
                "category": [6],
                "cleared": [7],
                "import_id": [8],
                "payee_id": [9],
                "category_id": [10],
                "approved": [11],
                "flag_color": [12],
            }
        )
        json_output = output_json_transactions(test_df)
        print(json_output)
        raise NotImplementedError


'''
    def test_valid_row(self):
        """Test making sure row has an outflow or an inflow"""
        config = fix_conf_params(self.cp, "test_row_format_default")
        b = B2YBank(config)

        for row, row_validity in [
            (["Pending", "Payee", "", "", "300", ""], False),
            (["28.09.2017", "Payee", "", "", "", "400"], False),
            (["28.09.2017", "Payee", "", "", "", ""], False),
            (["2017-09-28", "Payee", "", "", "300", ""], True),
            (["2017-09-28", "Payee", "", "", "", "400"], True),
            (["2017-09-28", "Payee", "", "", "", ""], False),
        ]:
            is_valid = b._remove_invalid_rows(row)
            self.assertEqual(is_valid, row_validity)

    def test_clean_monetary_values(self):
        """Test cleaning of outflow and inflow of unneeded characters"""
        config = fix_conf_params(self.cp, "test_row_format_default")
        b = B2YBank(config)

        for row, expected_row in [
            (
                ["28.09.2017", "Payee", "", "", "+ £300.01", ""],
                ["28.09.2017", "Payee", "", "", "300.01", ""],
            ),
            (
                ["28.09.2017", "Payee", "", "", "", "- $300"],
                ["28.09.2017", "Payee", "", "", "", "300"],
            ),
        ]:
            result_row = b._clean_monetary_values(row)
            self.assertCountEqual(expected_row, result_row)

    def test_auto_memo(self):
        """Test auto-filling empty memo field with payee data"""
        config = fix_conf_params(self.cp, "test_row_format_default")
        b = B2YBank(config)
        memo_index = b.config["output_columns"].index("Memo")

        for row, test_memo, fill_memo in [
            (["28.09.2017", "Payee", "", "", "300", ""], "", False),
            (["28.09.2017", "Payee", "", "Memo", "300", ""], "Memo", False),
            (["28.09.2017", "Payee", "", "", "300", ""], "Payee", True),
            (["28.09.2017", "Payee", "", "Memo", "", "400"], "Memo", True),
        ]:
            new_memo = b._auto_memo(row, fill_memo)[memo_index]
            self.assertEqual(test_memo, new_memo)

    def test_fix_outflow(self):
        """Test conversion of negative Inflow into Outflow"""
        config = fix_conf_params(self.cp, "test_row_format_default")
        b = B2YBank(config)

        for row, expected_row in [
            (
                ["28.09.2017", "Payee", "", "", "300", ""],
                ["28.09.2017", "Payee", "", "", "300", ""],
            ),
            (
                ["28.09.2017", "Payee", "", "", "", "-300"],
                ["28.09.2017", "Payee", "", "", "300", ""],
            ),
            (
                ["28.09.2017", "Payee", "", "", "", "300"],
                ["28.09.2017", "Payee", "", "", "", "300"],
            ),
        ]:
            result_row = b._fix_outflow(row)
            self.assertCountEqual(expected_row, result_row)

    def test_fix_inflow(self):
        """Test conversion of positive Outflow into Inflow"""
        config = fix_conf_params(self.cp, "test_row_format_default")
        b = B2YBank(config)

        for row, expected_row in [
            (
                ["28.09.2017", "Payee", "", "", "300", ""],
                ["28.09.2017", "Payee", "", "", "300", ""],
            ),
            (
                ["28.09.2017", "Payee", "", "", "+300", ""],
                ["28.09.2017", "Payee", "", "", "", "300"],
            ),
            (
                ["28.09.2017", "Payee", "", "", "", "300"],
                ["28.09.2017", "Payee", "", "", "", "300"],
            ),
        ]:
            result_row = b._fix_inflow(row)
            self.assertCountEqual(expected_row, result_row)

    """
    def test_fix_date(self):
        # todo

    def test_cd_flag_process():
        # todo
'''
