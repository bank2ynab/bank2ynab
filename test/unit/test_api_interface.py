from unittest.mock import patch

import pytest


class TestAPIInterface:
    @pytest.mark.skip(reason="Not tested yet.")
    def test_init(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not tested yet.")
    def test_api_read(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not tested yet.")
    def test_list_accounts(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not tested yet.")
    def test_access_api(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not tested yet.")
    @patch("api_interface.api_read")
    def test_get_budgets(self, mock_api_read):
        mock_api_read.return_values = [[{}, {}]]
        raise NotImplementedError

    @pytest.mark.skip(reason="Not tested yet.")
    def test_get_budget_accounts(self):
        raise NotImplementedError

    @pytest.mark.skip(reason="Not tested yet.")
    def test_post_transactions(self):
        raise NotImplementedError

    def fix_id_based_dicts(self):
        raise NotImplementedError
