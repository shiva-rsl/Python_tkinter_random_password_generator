import unittest
from unittest.mock import patch

import utils


def make_settings(**overrides):
    settings = {
        "password_length": 12,
        "uppercase": True,
        "lowercase": True,
        "space": False,
        "minus": False,
        "underline": False,
        "digit": True,
        "symbol": True,
        "bracket": False,
    }
    settings.update(overrides)
    return settings


class TestPasswordLength(unittest.TestCase):
    def test_minimum_length_is_valid(self):
        self.assertTrue(utils.is_valid_password_length(utils.MIN_PASSWORD_LENGTH))

    def test_maximum_length_is_valid(self):
        self.assertTrue(utils.is_valid_password_length(utils.MAX_PASSWORD_LENGTH))

    def test_length_below_minimum_is_invalid(self):
        self.assertFalse(utils.is_valid_password_length(utils.MIN_PASSWORD_LENGTH - 1))

    def test_length_above_maximum_is_invalid(self):
        self.assertFalse(utils.is_valid_password_length(utils.MAX_PASSWORD_LENGTH + 1))


class TestCharacterSettings(unittest.TestCase):
    def test_enabled_character_types_preserves_defined_order(self):
        settings = make_settings(uppercase=True, lowercase=False, digit=True, symbol=True)
        self.assertEqual(
            utils.enabled_character_types(settings),
            ["uppercase", "digit", "symbol"],
        )

    def test_no_enabled_types_returns_empty_list(self):
        settings = make_settings(
            uppercase=False, lowercase=False, digit=False, symbol=False,
            minus=False, underline=False, space=False, bracket=False,
        )
        self.assertEqual(utils.enabled_character_types(settings), [])

    def test_build_character_pool_combines_enabled_sets(self):
        settings = make_settings(
            uppercase=False, lowercase=False, digit=True, symbol=False,
            minus=True, underline=False, space=False, bracket=False,
        )
        self.assertEqual(utils.build_character_pool(settings), utils.CHARSETS["digit"] + "-")

    def test_calculate_password_range_matches_pool_size(self):
        settings = make_settings()
        self.assertEqual(
            utils.calculate_password_range(settings),
            len(utils.build_character_pool(settings)),
        )

    def test_analyze_selected_password_detects_character_types(self):
        result = utils.analyze_selected_password("Ab3- _[]")
        self.assertEqual(result["password_length"], 8)
        self.assertTrue(result["uppercase"])
        self.assertTrue(result["lowercase"])
        self.assertTrue(result["digit"])
        self.assertTrue(result["minus"])
        self.assertTrue(result["space"])
        self.assertTrue(result["underline"])
        self.assertTrue(result["bracket"])

    def test_analyze_empty_password(self):
        result = utils.analyze_selected_password("")
        self.assertEqual(result["password_length"], 0)
        self.assertTrue(all(result[key] is False for key in utils.CHARSETS))


class TestPasswordGeneration(unittest.TestCase):
    def test_generated_password_has_requested_length(self):
        for length in (utils.MIN_PASSWORD_LENGTH, 12, utils.MAX_PASSWORD_LENGTH):
            with self.subTest(length=length):
                password = utils.random_password_generator(make_settings(password_length=length))
                self.assertEqual(len(password), length)

    def test_generated_password_uses_only_enabled_characters(self):
        settings = make_settings(
            password_length=16, uppercase=False, lowercase=False,
            digit=True, symbol=False, minus=False, underline=False,
            space=False, bracket=False,
        )
        password = utils.random_password_generator(settings)
        self.assertTrue(password)
        self.assertTrue(all(char in utils.CHARSETS["digit"] for char in password))

    def test_each_enabled_type_is_present_when_length_allows(self):
        settings = make_settings(password_length=12)
        password = utils.random_password_generator(settings)
        analysis = utils.analyze_selected_password(password)
        for option in utils.enabled_character_types(settings):
            with self.subTest(option=option):
                self.assertTrue(analysis[option])

    def test_no_character_type_raises_value_error(self):
        settings = make_settings(
            uppercase=False, lowercase=False, digit=False, symbol=False,
            minus=False, underline=False, space=False, bracket=False,
        )
        with self.assertRaisesRegex(ValueError, "At least one character type"):
            utils.random_password_generator(settings)

    def test_invalid_length_raises_value_error(self):
        for length in (utils.MIN_PASSWORD_LENGTH - 1, utils.MAX_PASSWORD_LENGTH + 1):
            with self.subTest(length=length):
                with self.assertRaises(ValueError):
                    utils.random_password_generator(make_settings(password_length=length))

    def test_short_password_length_does_not_require_every_enabled_type(self):
        settings = make_settings(password_length=utils.MIN_PASSWORD_LENGTH)
        password = utils.random_password_generator(settings)
        self.assertEqual(len(password), utils.MIN_PASSWORD_LENGTH)
        self.assertTrue(all(char in utils.build_character_pool(settings) for char in password))

    @patch("utils.secrets.choice", side_effect=lambda seq: seq[0])
    @patch("utils._secure_shuffle")
    def test_generator_selects_one_character_from_each_enabled_type(self, mock_shuffle, mock_choice):
        settings = make_settings(password_length=8, uppercase=True, lowercase=True,
                                 digit=False, symbol=False, minus=False,
                                 underline=False, space=False, bracket=False)
        password = utils.random_password_generator(settings)
        self.assertIn(utils.CHARSETS["uppercase"][0], password)
        self.assertIn(utils.CHARSETS["lowercase"][0], password)
        mock_shuffle.assert_called_once()


class TestEntropyAndStrength(unittest.TestCase):
    def test_entropy_uses_password_length_and_pool_size(self):
        settings = make_settings()
        password = "A" * 10
        expected = 10 * __import__("math").log2(len(utils.build_character_pool(settings)))
        self.assertAlmostEqual(utils.calculate_password_entropy(password, settings), expected)

    def test_entropy_is_zero_when_pool_has_one_or_fewer_characters(self):
        settings = make_settings(
            uppercase=False, lowercase=False, digit=False, symbol=False,
            minus=True, underline=False, space=False, bracket=False,
        )
        self.assertEqual(utils.calculate_password_entropy("--------", settings), 0.0)

    def test_strength_thresholds(self):
        cases = [
            (27.99, "🔴 Very Weak", 10),
            (28, "🟠 Weak", 30),
            (36, "🟡 Fair", 55),
            (60, "🟣 Strong", 80),
            (128, "🟢 Very Strong", 100),
        ]
        for entropy, label, score in cases:
            with self.subTest(entropy=entropy):
                result = utils.evaluate_password_strength(entropy)
                self.assertEqual(result["label"], label)
                self.assertEqual(result["score"], score)
                self.assertIn("color", result)

    def test_calculate_password_strength_returns_score_label_color(self):
        settings = make_settings()
        result = utils.calculate_password_strength("A" * 12, settings)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], int)
        self.assertIsInstance(result[1], str)
        self.assertIsInstance(result[2], str)


if __name__ == "__main__":
    unittest.main()
