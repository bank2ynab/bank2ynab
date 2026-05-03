from unittest.mock import MagicMock, patch

import pytest

from bank2ynab.ynab_api import YNAB_API, apply_mapping, generate_name_id_list


def make_config_handler(api_token: str | None) -> MagicMock:
    mock_config = MagicMock()
    mock_config.get.return_value = api_token
    handler = MagicMock()
    handler.config = mock_config
    return handler


class TestYNAB_API:
    @patch("bank2ynab.ynab_api.ConfigHandler")
    def test_init_raises_when_api_token_missing(self, mock_config_handler_cls):
        mock_config_handler_cls.return_value = make_config_handler("")
        with pytest.raises(ValueError, match="No YNAB API token"):
            YNAB_API(config_object=make_config_handler(""))

    @patch("bank2ynab.ynab_api.ConfigHandler")
    def test_init_raises_when_api_token_none(self, mock_config_handler_cls):
        mock_config_handler_cls.return_value = make_config_handler(None)
        with pytest.raises(ValueError):
            YNAB_API(config_object=make_config_handler(None))

    @pytest.mark.skip(reason="Not tested yet.")
    def test_init(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not tested yet.")
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
        assert apply_mapping(test_data, test_mapping) == expected_output

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
        assert generate_name_id_list(test_dict) == expected_output

    @pytest.mark.skip(reason="Not tested yet.")
    def test_save_account_selection(self):
        raise NotImplementedError
