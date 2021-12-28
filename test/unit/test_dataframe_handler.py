import unittest
from unittest import TestCase

import pandas as pd
import pandas.testing
from bank2ynab.dataframe_handler import (
    add_missing_columns,
    auto_memo,
    auto_payee,
    cd_flag_process,
    clean_monetary_values,
    fix_amount,
    merge_duplicate_columns,
    output_json_transactions,
    remove_invalid_rows,
)
from pandas._libs.missing import NA


class TestDataframeHandler(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_merge_duplicate_columns(self):
        """Check that merging of duplicate columns works correctly."""
        test_dfs = [
            {
                # test no duplicate columns
                "data": {
                    "Amount": [4, 3, 2, 1],
                    "Payee": ["four", "three", "two", "one"],
                },
                "input_cols": ["Amount", "Payee"],
                "desired_output": ["Amount", "Payee"],
            },
            {
                # test two duplicate columns
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
            with self.subTest(
                "Test different amount of duplicate columns.",
                test=test,
            ):
                test_df = merge_duplicate_columns(
                    pd.DataFrame(test["data"]),
                    test["input_cols"],
                )
                self.assertCountEqual(
                    test["desired_output"],
                    list(test_df),
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
            with self.subTest(
                "Test different amount of missing columns.", dataset=dataset
            ):
                test_df = pd.DataFrame(dataset)
                test_df = add_missing_columns(
                    test_df, list(test_df), desired_cols
                )
                # check if column names contain all desired values
                self.assertCountEqual(desired_cols, list(test_df))

    def test_cd_flag_process(self):
        """Test correct application of inflow/outflow flags."""
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
            with self.subTest(
                "Test different input/output flag scenarios.", dataset=dataset
            ):
                test_df = pd.DataFrame(dataset["data"])
                test_df = cd_flag_process(test_df, dataset["cd_flags"])
                self.assertEqual(
                    dataset["target_inflow"], test_df["Inflow"].iloc[0]
                )

    def test_fix_amount(self):
        """
        Test fixing of negative inflows/outflows & amount column creation.
        """
        initial_df = pd.DataFrame(
            {"Inflow": [10, -20, 0, 0, 0], "Outflow": [0, 0, -100, 0, 0]}
        )
        test_df = fix_amount(initial_df, 1)
        desired_output = pd.DataFrame(
            {
                "Inflow": [10, 0, 100, 0, 0],
                "Outflow": [0, 20, 0, 0, 0],
                "amount": [10000, -20000, 100000, 0, 0],
            }
        )
        for column in desired_output.keys():
            with self.subTest(
                "Test each column's negative inflow/outflow processing.",
                column=column,
            ):
                pandas.testing.assert_series_equal(
                    desired_output[column].astype(float),
                    test_df[column],
                )

    def test_currency_fix(self):
        """Test currency conversion."""
        initial_df = pd.DataFrame(
            {"Inflow": [10, -20, 0, 0, 0], "Outflow": [0, 0, -100, 0, 0]}
        )
        test_df = fix_amount(initial_df, 4)
        desired_output = pd.DataFrame(
            {
                "Inflow": [2.5, 0, 25, 0, 0],
                "Outflow": [0, 5, 0, 0, 0],
                "amount": [2500, -5000, 25000, 0, 0],
            }
        )
        for column in desired_output.keys():
            with self.subTest(
                "Test each column's currency conversion.",
                column=column,
            ):
                pandas.testing.assert_series_equal(
                    desired_output[column].astype(float),
                    test_df[column],
                )

    def test_clean_monetary_values(self):
        """Test string format fixing for monetary values."""
        initial_data = pd.Series(
            data={
                "a": "10",
                "b": "10,50",
                "c": "$77.77",
                "d": "€88.88",
                "e": "99....!.99",
                "f": "20..10",
                "g": "10,,0",
                "h": "0",
                "i": "+40",
                "j": "-30.30",
            }
        )
        desired_output = pd.Series(
            data={
                "a": 10,
                "b": 10.50,
                "c": 77.77,
                "d": 88.88,
                "e": 99.99,
                "f": 20.10,
                "g": 10,
                "h": 0,
                "i": 40,
                "j": -30.30,
            }
        )
        test_data = clean_monetary_values(initial_data)
        pandas.testing.assert_series_equal(
            desired_output,
            test_data,
        )

    def test_remove_invalid_rows(self):
        initial_df = pd.DataFrame(
            {
                "Inflow": [10, 0, 30, 0, 66, NA, NA],
                "Outflow": [0, 20, 40, 100, 0, NA, 77],
                "Payee": ["a", "b", "c", "d", "e", "f", "g"],
                "Date": [
                    "28.09.2017",
                    "28.09.2017",
                    "2017-09-28",
                    "2017-09-28",
                    NA,
                    "2017-09-28",
                    "2017-10-28",
                ],
            }
        )
        desired_output = pd.DataFrame(
            {
                "Inflow": [10, 0, 30, 0, 0],
                "Outflow": [0, 20, 40, 100, 77],
                "Payee": ["a", "b", "c", "d", "g"],
                "Date": [
                    "28.09.2017",
                    "28.09.2017",
                    "2017-09-28",
                    "2017-09-28",
                    "2017-10-28",
                ],
            }
        ).set_index("Date")

        test_df = remove_invalid_rows(initial_df).set_index("Date")
        del test_df["index"]
        pandas.testing.assert_frame_equal(desired_output, test_df, False)

    def test_auto_memo(self):
        # TODO establish if it's even possible for an empty string to
        # make it this far - maybe it's always NA?
        initial_df = pd.DataFrame(
            {
                "Payee": ["A", "B", "C", NA],
                "Memo": ["Complete Memo", NA, NA, NA],
                "Expected Unfilled Memo": ["Complete Memo", NA, NA, NA],
                "Expected Filled Memo": ["Complete Memo", "B", "C", NA],
            }
        )

        test_df_no_fill = auto_memo(initial_df, False)

        pandas.testing.assert_series_equal(
            initial_df["Expected Unfilled Memo"],
            test_df_no_fill["Memo"],
            check_names=False,  # type:ignore
        )
        test_df_fill = auto_memo(initial_df, True)

        pandas.testing.assert_series_equal(
            initial_df["Expected Filled Memo"],
            test_df_fill["Memo"],
            check_names=False,  # type:ignore
        )

    def test_auto_payee(self):
        initial_df = pd.DataFrame(
            {
                "Payee": ["A", NA, NA],
                "Memo": ["Complete Memo", "Payee Memo", NA],
                "Expected Payee": ["A", "Payee Memo", NA],
            }
        )

        test_df = auto_payee(initial_df)

        pandas.testing.assert_series_equal(
            initial_df["Expected Payee"],
            test_df["Payee"],
            check_names=False,  # type:ignore
        )

    @unittest.skip("Test not implemented yet")
    def test_fix_date(self):
        # test_df["Date"] = fix_date()
        raise NotImplementedError

    @unittest.skip("Test not implemented yet")
    def test_fill_api_columns(self):
        # test_df = fill_api_columns()
        raise NotImplementedError

    @unittest.skip("Test not implemented yet")
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
