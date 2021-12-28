from unittest import TestCase

import pandas as pd
import pandas.testing
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
        """Test auto-filling of memo field with payee if allowed."""
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
        """Test auto filling of Payee with Memo info."""
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

    def test_fix_date(self):
        test_params = [
            {
                "date_format": "%Y-%m-%d",
                "data": {
                    "a": "2021-10-01",
                    "b": "2021-09-21",
                    "c": "2021-02-29",
                    "d": "2001-10-01",
                },
            },
            {
                "date_format": "%Y%m%d",
                "data": {
                    "a": "20211001",
                    "b": "20210921",
                    "c": "20210229",
                    "d": "20011001",
                },
            },
            {
                "date_format": "%d.%m.%Y",
                "data": {
                    "a": "01.10.2021",
                    "b": "21.09.2021",
                    "c": "29.02.2021",
                    "d": "01.10.2001",
                },
            },
            {
                "date_format": "%Y-%m-%d %H:%M:%S",
                "data": {
                    "a": "2021-10-01 01:02:03",
                    "b": "2021-09-21 01:32:02",
                    "c": "2021-02-29 01:59:44",
                    "d": "2001-10-01 01:10:35",
                },
            },
        ]
        desired_output = pd.Series(
            data={
                "a": "2021-10-01",
                "b": "2021-09-21",
                "c": NA,
                "d": "2001-10-01",
            }
        )
        for test in test_params:
            with self.subTest(test=test):
                test_series = fix_date(
                    pd.Series(data=test["data"]), test["date_format"]
                )
                pandas.testing.assert_series_equal(desired_output, test_series)

    def test_fill_api_columns(self):
        """Test correct API column filling."""
        api_cols = [
            "account_id",
            "date",
            "payee_name",
            "amount",
            "memo",
            "category",
            "cleared",
            "import_id",
            "payee_id",
            "category_id",
            "approved",
            "flag_color",
        ]
        really_long_payee = "a" * 60
        truncated_payee = really_long_payee[:50]
        really_long_memo = "m" * 200
        truncated_memo = really_long_memo[:100]
        initial_df = pd.DataFrame(
            {
                "account_id": ["", "", "", ""],
                "Date": [
                    "2017-09-28",
                    "2017-09-28",
                    "2017-09-28",
                    "2017-10-28",
                ],
                "Payee": ["Test 1", "Test 2", "Test 3", really_long_payee],
                "amount": [-1000, 25000, 25000, 0],
                "Memo": ["Test Memo", "", really_long_memo, "Test Memo"],
            }
        )

        expected_output = pd.DataFrame(
            {
                "account_id": ["", "", "", ""],
                "date": [
                    "2017-09-28",
                    "2017-09-28",
                    "2017-09-28",
                    "2017-10-28",
                ],
                "payee_name": ["Test 1", "Test 2", "Test 3", truncated_payee],
                "amount": [-1000, 25000, 25000, 0],
                "memo": ["Test Memo", "", truncated_memo, "Test Memo"],
                "category": ["", "", "", ""],
                "cleared": ["cleared", "cleared", "cleared", "cleared"],
                "import_id": [
                    "YNAB:-1000:2017-09-28:1",
                    "YNAB:25000:2017-09-28:1",
                    "YNAB:25000:2017-09-28:2",
                    "YNAB:0:2017-10-28:1",
                ],
                "payee_id": [None, None, None, None],
                "category_id": [None, None, None, None],
                "approved": [False, False, False, False],
                "flag_color": [None, None, None, None],
            }
        )

        test_df = fill_api_columns(initial_df)
        pandas.testing.assert_frame_equal(expected_output, test_df[api_cols])

    def test_output_json_transactions(self):
        """Test that the JSON output is in the correct format."""
        test_df = pd.DataFrame(
            {
                "account_id": ["", "", "", ""],
                "date": [
                    "2017-09-28",
                    "2017-09-28",
                    "2017-09-28",
                    "2017-10-28",
                ],
                "payee_name": ["Test 1", "Test 2", "Test 3", "Test 4"],
                "amount": [-1000, 25000, 25000, 0],
                "memo": ["Test Memo", "", "Test Memo", "Test Memo"],
                "category": ["", "", "", ""],
                "cleared": ["cleared", "cleared", "cleared", "cleared"],
                "import_id": [
                    "YNAB:-1000:2017-09-28:1",
                    "YNAB:25000:2017-09-28:1",
                    "YNAB:25000:2017-09-28:2",
                    "YNAB:0:2017-10-28:1",
                ],
                "payee_id": [None, None, None, None],
                "category_id": [None, None, None, None],
                "approved": [False, False, False, False],
                "flag_color": [None, None, None, None],
            }
        )
        json_output = output_json_transactions(test_df)

        expected_output = (
            '[{"account_id":"","date":"2017-09-28","payee_name":"Test'
            ' 1","amount":-1000,"memo":"Test'
            ' Memo","category":"","cleared":"cleared","import_id":'
            '"YNAB:-1000:2017-09-28:1","payee_id":null,"category_id":null,'
            '"approved":false,"flag_color":null},{"account_id":"",'
            '"date":"2017-09-28","payee_name":"Test'
            ' 2","amount":25000,"memo":"","category":"","cleared":'
            '"cleared","import_id":"YNAB:25000:2017-09-28:1",'
            '"payee_id":null,"category_id":null,"approved":false,'
            '"flag_color":null},{"account_id":"","date":"2017-09-28",'
            '"payee_name":"Test 3","amount":25000,"memo":"Test Memo",'
            '"category":"","cleared":"cleared","import_id":'
            '"YNAB:25000:2017-09-28:2","payee_id":null,"category_id":null,'
            '"approved":false,"flag_color":null},{"account_id":"",'
            '"date":"2017-10-28","payee_name":"Test'
            ' 4","amount":0,"memo":"Test'
            ' Memo","category":"","cleared":"cleared",'
            '"import_id":"YNAB:0:2017-10-28:1","payee_id":null,'
            '"category_id":null,"approved":false,"flag_color":null}]'
        )

        self.assertEqual(expected_output, json_output["transactions"])
