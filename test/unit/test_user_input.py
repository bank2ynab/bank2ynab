from unittest.mock import call, patch

from bank2ynab.user_input import display_options, get_int_input, get_user_input

TEST_OPTIONS = [
    ["Bank 1", "ID 1"],
    ["Bank 2", "ID 2"],
    ["Bank 3", "ID 3"],
]


class TestUserInput:
    @patch("builtins.input")
    def test_get_user_input(self, mock_input):
        """Test correct return of option string from user input."""
        test_message = "Here's a list of banks to choose from."
        test_inputs = [1, 2, 3]
        mock_input.side_effect = test_inputs
        for test_input in test_inputs:
            return_string = get_user_input(TEST_OPTIONS, test_message)
            assert return_string == TEST_OPTIONS[test_input - 1][1]

    @patch("builtins.print")
    def test_option_display(self, mock_print):
        """Test correct list display of options."""
        display_options(TEST_OPTIONS)
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
        mock_input.side_effect = test_inputs

        test_outputs = [get_int_input(1, 5, "Testing input") for _ in expected_output]
        assert test_outputs == expected_output
