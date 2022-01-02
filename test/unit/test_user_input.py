from unittest import TestCase
from unittest.mock import call, patch

from bank2ynab.user_input import display_options, get_int_input, get_user_input


class TestUserInput(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    @patch("builtins.input")
    def test_get_user_input(self, mock_input):
        """Test correct return of option string from user input."""
        test_options = [
            ["Bank 1", "ID 1"],
            ["Bank 2", "ID 2"],
            ["Bank 3", "ID 3"],
        ]
        test_message = "Here's a list of banks to choose from."
        test_inputs = [1, 2, 3]
        mock_input.side_effect = test_inputs
        for test_input in test_inputs:
            with self.subTest(
                "Test different integer inputs.", test_input=test_input
            ):
                return_string = get_user_input(test_options, test_message)
                self.assertEqual(
                    test_options[test_input - 1][1], return_string
                )

    @patch("builtins.print")
    def test_option_display(self, mock_print):
        """Test correct list display of options."""
        test_options = [
            ["Bank 1", "ID 1"],
            ["Bank 2", "ID 2"],
            ["Bank 3", "ID 3"],
        ]
        display_options(test_options)
        calls = [
            call("\n"),
            call("| 1 | Bank 1"),
            call("| 2 | Bank 2"),
            call("| 3 | Bank 3"),
        ]
        mock_print.assert_has_calls(calls, any_order=False)

    @patch("builtins.input")
    def test_get_int_input(self, mock_input):
        """Test input validation."""
        test_inputs = [1, 99, 2, -99, 1, "abacus", 5]
        expected_output = [1, 2, 1, 5]
        test_outputs = []
        mock_input.side_effect = test_inputs

        for test in expected_output:
            test_outputs.append(get_int_input(1, 5, "Testing input"))
        self.assertListEqual(expected_output, test_outputs)
