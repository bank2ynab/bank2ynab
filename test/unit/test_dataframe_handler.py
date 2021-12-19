from unittest import TestCase


class TestDataframeHandler(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()


'''
    def test_rearrange_columns(self):
        """Check output row is the same across different formats"""
        # todo: something where the row format is invalid
        # if you need more tests, add sections to test.conf & specify them here
        for section_name in [
            "test_row_format_default",
            "test_row_format_neg_inflow",
            "test_row_format_CD_flag",
            "test_row_format_invalid",
        ]:
            config = fix_conf_params(self.cp, section_name)
            b = B2YBank(config)
            for f in b.get_files():
                output_data = b.read_data(f)
                # test the same two rows in each scenario
                for row, expected_row in [
                    (
                        23,
                        [
                            "2017-09-28",
                            "HOFER DANKT  0527  K2   28.09. 17:17",
                            "",
                            "HOFER DANKT  0527  K2   28.09. 17:17",
                            "44.96",
                            "",
                        ],
                    ),
                    (
                        24,
                        [
                            "2017-09-28",
                            "SOFTWARE Wien",
                            "",
                            "SOFTWARE Wien",
                            "",
                            "307.67",
                        ],
                    ),
                ]:
                    result_row = output_data[row]

                    self.assertCountEqual(expected_row, result_row)

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
