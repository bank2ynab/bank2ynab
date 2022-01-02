from unittest import TestCase
from unittest.mock import patch


class TestAPIInterface(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_init(self):
        pass

    def test_api_read(self):
        raise NotImplementedError

    def test_list_accounts(self):
        raise NotImplementedError

    @patch("api_interface.api_read")
    def test_list_budgets(self, mock_api_read):
        mock_api_read.return_values = [[{}, {}]]
        raise NotImplementedError

    def test_post_transactions(self):
        raise NotImplementedError

    def fix_id_based_dicts(self):
        raise NotImplementedError
