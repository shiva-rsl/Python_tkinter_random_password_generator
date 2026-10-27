import unittest
from unittest.mock import patch

import random_password_generator_CLI as cli
import utils


def make_settings():
    return {
        "password_length": 8,
        "uppercase": True,
        "lowercase": True,
        "space": False,
        "minus": False,
        "underline": False,
        "digit": True,
        "symbol": True,
        "bracket": False,
    }


class TestCLIInput(unittest.TestCase):
    @patch("builtins.input", return_value="")
    def test_default_password_length_is_accepted(self, mock_input):
        self.assertEqual(cli.get_user_password_length("Length", 12), 12)

    @patch("builtins.input", side_effect=["abc", "7", "31", "10"])
    def test_invalid_lengths_are_reprompted(self, mock_input):
        self.assertEqual(cli.get_user_password_length("Length", 8), 10)
        self.assertEqual(mock_input.call_count, 4)

    @patch("builtins.input", return_value="y")
    def test_yes_setting_returns_true(self, mock_input):
        self.assertTrue(cli.get_user_password_settings("uppercase", False))

    @patch("builtins.input", return_value="n")
    def test_no_setting_returns_false(self, mock_input):
        self.assertFalse(cli.get_user_password_settings("uppercase", True))

    @patch("builtins.input", side_effect=["maybe", "y"])
    def test_invalid_boolean_input_is_reprompted(self, mock_input):
        self.assertTrue(cli.get_user_password_settings("uppercase", False))
        self.assertEqual(mock_input.call_count, 2)


class TestCLILogic(unittest.TestCase):
    def test_colorize_outputs_returns_plain_text_for_unknown_type(self):
        self.assertEqual(cli.colorize_outputs("unknown", "hello"), "hello")

    def test_generated_password_respects_settings(self):
        settings = make_settings()
        password = cli.get_generated_password(settings)
        self.assertEqual(len(password), settings["password_length"])
        self.assertTrue(all(c in utils.build_character_pool(settings) for c in password))

    @patch.object(cli, "get_generated_password", return_value="Ab3!xyZ9")
    @patch.object(cli, "calculate_password_entropy", return_value=42.0)
    @patch.object(cli, "evaluate_password_strength", return_value={"label": "🟡 Fair", "score": 55, "color": "#EFE63E"})
    def test_generate_password_with_metrics_returns_expected_tuple(
        self, mock_strength, mock_entropy, mock_password
    ):
        result = cli.generate_password_with_metrics(make_settings())
        self.assertEqual(result, ("Ab3!xyZ9", 42.0, "🟡 Fair"))
        mock_entropy.assert_called_once_with("Ab3!xyZ9", make_settings())

    @patch("builtins.print")
    @patch.object(cli, "generate_password_with_metrics", side_effect=ValueError("bad settings"))
    def test_print_metrics_handles_generation_error(self, mock_generate, mock_print):
        cli.print_generated_password_entropy_strength(make_settings())
        mock_print.assert_called_once()
        self.assertIn("bad settings", mock_print.call_args.args[0])

    @patch("builtins.input", side_effect=["n"])
    @patch.object(cli, "print_generated_password_entropy_strength")
    def test_regenerate_stops_when_user_enters_no(self, mock_print, mock_input):
        cli.regenerate_random_password(make_settings())
        mock_print.assert_not_called()


if __name__ == "__main__":
    unittest.main()
