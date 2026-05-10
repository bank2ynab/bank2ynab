import os
import tempfile
import unittest
from unittest import TestCase

import pandas as pd
import pandas.testing
from pandas._libs.missing import NA

from bank2ynab.dataframe_handler import (
    add_missing_columns,
    read_csv,
    apply_payee_mappings,
    auto_memo,
    auto_payee,
    cd_flag_process,
    clean_monetary_values,
    clean_strings,
    combine_dfs,
    fill_api_columns,
    fill_empty_dates,
    fix_amount,
    fix_date,
    merge_duplicate_columns,
    remove_invalid_rows,
)


class TestDataframeHandler(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_read_csv_quoted_delimiter(self):
        """Delimiter inside a quoted field must not split the field."""
        csv_content = 'Date;Payee;Amount\n2024-01-01;"Smith; Jones Ltd";100\n'
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(csv_content)
            tmp_path = f.name
        try:
            df = read_csv(
                file_path=tmp_path,
                delim=";",
                header_rows=1,
                footer_rows=0,
                encod="utf-8",
            )
            self.assertEqual(df.shape[1], 3)
            self.assertEqual(df.iloc[0, 1], "Smith; Jones Ltd")
        finally:
            os.unlink(tmp_path)

    @unittest.skip("Not tested yet.")
    def test_parse_data(self):
        """Test full parsing workflow."""
        """
        test_dataframe = DataframeHandler
        self.input_columns = input_columns
        self.output_columns = output_columns
        self.api_columns = api_columns
        self.cd_flags = cd_flags
        self.date_format = date_format
        self.fill_memo = fill_memo
        self.currency_fix = currency_fix
        """

        raise NotImplementedError

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
                "desired_column_output": ["four", "three", "two", "one"],
                "desired_output": ["Amount", "Payee"],
                "merged_column": "Payee",
            },
            {
                # test two duplicate columns
                "data": {
                    "Amount": [4, 3, 2, 1],
                    "Payee": ["four", "three", "two", "one"],
                    "Memo": ["four", "three", "two", "one"],
                },
                "input_cols": ["Amount", "Payee", "Payee"],
                "desired_column_output":["four four", "three three", "two two", "one one"],
                "desired_output": ["Amount", "Payee", "Payee 0"],
                "merged_column": "Payee",
            },
            {
                # test duplicate numeric columns with NaN values
                "data": {
                    "Date": ["2024-01-01", "2024-01-02"],
                    "skip": [float("nan"), float("nan")],
                    "Memo": [float("nan"), "flagged"],
                },
                "input_cols": ["Date", "skip", "skip"],
                "desired_column_output": ["", "flagged"],
                "desired_output": ["Date", "skip", "skip 0"],
                "merged_column": "skip",
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
                self.assertCountEqual(
                    test["desired_column_output"],
                    test_df[test["merged_column"]]
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
                    test_df, list(test_df), desired_cols  # type: ignore
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
        desired_output["Inflow"] = desired_output["Inflow"].astype(float)
        desired_output["Outflow"] = desired_output["Outflow"].astype(float)
        desired_output["amount"] = desired_output["amount"].astype(int)
        for column in desired_output.keys():
            with self.subTest(
                "Test each column's negative inflow/outflow processing.",
                column=column,
            ):
                pandas.testing.assert_series_equal(
                    desired_output[column],
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
            },
        )
        desired_output["Inflow"] = desired_output["Inflow"].astype(float)
        desired_output["Outflow"] = desired_output["Outflow"].astype(float)
        desired_output["amount"] = desired_output["amount"].astype(int)
        for column in desired_output.keys():
            with self.subTest(
                "Test each column's currency conversion.",
                column=column,
            ):
                pandas.testing.assert_series_equal(
                    desired_output[column],
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
                "Inflow": [10, 0, 30, 0, 66, NA, NA, 0],
                "Outflow": [0, 20, 40, 100, 0, NA, 77, 0],
                "amount": [10, -20, -10, -100, 66, 0, -77, 0],
                "Payee": ["a", "b", "c", "d", "e", "f", "g", "h"],
                "Date": [
                    "28.09.2017",
                    "28.09.2017",
                    "2017-09-28",
                    "2017-09-28",
                    NA,
                    "2017-09-28",
                    "2017-10-28",
                    "2017-10-29",
                ],
            }
        )
        desired_output = pd.DataFrame(
            {
                "Inflow": [10, 0, 30, 0, 0],
                "Outflow": [0, 20, 40, 100, 77],
                "amount": [10, -20, -10, -100, -77],
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

    def test_remove_invalid_rows_with_string_dtype_columns(self):
        initial_df = pd.DataFrame(
            {
                "Inflow": [10, NA],
                "Outflow": [0, 0],
                "amount": [10, 0],
                "Payee": pd.Series(["a", NA], dtype="string"),
                "Memo": pd.Series([NA, "flag"], dtype="string"),
                "Date": pd.Series(["2017-09-28", "2017-09-29"], dtype="string"),
            }
        )

        test_df = remove_invalid_rows(initial_df)

        self.assertEqual(len(test_df), 1)
        self.assertEqual(test_df.iloc[0]["Payee"], "a")
        self.assertTrue(pd.isna(test_df.iloc[0]["Memo"]))

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

    def test_clean_strings(self):
        test_strings = [
            ["Normal", "Normal"],
            ["Extra internal    whitespace", "Extra Internal Whitespace"],
            ["      Extra leading whitespace", "Extra Leading Whitespace"],
            ["Extra trailing whitespace   ", "Extra Trailing Whitespace"],
            [r"Non alphanumeric \ ! @", "Non Alphanumeric"],
            ["RanDom CAPITAL letters", "Random Capital Letters"],
            ["New Line\nIn The String", "New Line In The String"],
            [
                "Ðö nøt rēmove ácçeñtéd chäråcterß",
                "Ðö Nøt Rēmove Ácçeñtéd Chäråcterß",
            ],
        ]
        for test in test_strings:
            with self.subTest(
                "Test different types of string input.", test=test
            ):
                test_series = pd.Series(data={1: test[0]})
                desired_output = pd.Series(data={1: test[1]})
                test_output = clean_strings(test_series)
                pandas.testing.assert_series_equal(desired_output, test_output)

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

    def test_fill_empty_dates(self):
        """Test filling in of empty date values."""
        test_series = pd.Series(
            data={
                "a": "2021-10-01",
                "b": "2021-09-21",
                "c": "",
                "d": "2001-10-01",
            }
        )

        target_filled_series = pd.Series(
            data={
                "a": "2021-10-01",
                "b": "2021-09-21",
                "c": "2021-09-21",
                "d": "2001-10-01",
            }
        )

        pandas.testing.assert_series_equal(
            test_series, fill_empty_dates(test_series, False)
        )
        pandas.testing.assert_series_equal(
            target_filled_series, fill_empty_dates(test_series, True)
        )

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
            # "payee_id",
            # "category_id",
            # "approved",
            # "flag_color",
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
                # "payee_id": [None, None, None, None],
                # "category_id": [None, None, None, None],
                # "approved": [False, False, False, False],
                # "flag_color": [None, None, None, None],
            }
        )

        test_df = fill_api_columns(initial_df)
        pandas.testing.assert_frame_equal(expected_output, test_df[api_cols])

    def test_combine_dfs(self):
        dfs = [
            pd.DataFrame({"Col1": [45], "Col2": [36]}),
            pd.DataFrame({"Col1": [55], "Col2": [98]}),
        ]
        expected_output = pd.DataFrame({"Col1": [45, 55], "Col2": [36, 98]})
        test_output = combine_dfs(dfs)
        pandas.testing.assert_frame_equal(expected_output, test_output)

    def test_apply_payee_mappings_match(self):
        """Exact match replaces payee."""
        df = pd.DataFrame({"Payee": ["PAYPAL (EUROPE) S.A.R.L ET CIE,S.C.A."]})
        result = apply_payee_mappings(df, {"PAYPAL (EUROPE)": "PayPal"})
        self.assertEqual(result["Payee"].iloc[0], "PayPal")

    def test_apply_payee_mappings_no_match(self):
        """Non-matching payee is left unchanged."""
        df = pd.DataFrame({"Payee": ["AMAZON EU"]})
        result = apply_payee_mappings(df, {"PAYPAL": "PayPal"})
        self.assertEqual(result["Payee"].iloc[0], "AMAZON EU")

    def test_apply_payee_mappings_case_insensitive(self):
        """Matching is case-insensitive."""
        df = pd.DataFrame({"Payee": ["paypal europe"]})
        result = apply_payee_mappings(df, {"PAYPAL": "PayPal"})
        self.assertEqual(result["Payee"].iloc[0], "PayPal")

    def test_apply_payee_mappings_first_match_wins(self):
        """First matching mapping wins when multiple keys match."""
        df = pd.DataFrame({"Payee": ["PAYPAL AMAZON"]})
        result = apply_payee_mappings(
            df, {"PAYPAL": "PayPal", "AMAZON": "Amazon"}
        )
        self.assertEqual(result["Payee"].iloc[0], "PayPal")

    def test_apply_payee_mappings_empty(self):
        """Empty mappings dict leaves payee unchanged."""
        df = pd.DataFrame({"Payee": ["SOME PAYEE"]})
        result = apply_payee_mappings(df, {})
        self.assertEqual(result["Payee"].iloc[0], "SOME PAYEE")
