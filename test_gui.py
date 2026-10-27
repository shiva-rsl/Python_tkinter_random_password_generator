import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import random_password_generator_GUI as gui


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


class TestGUIHelpers(unittest.TestCase):
    def setUp(self):
        gui.password_history.clear()
        gui.password_option.clear()
        gui.password_option.update(make_settings())

    def tearDown(self):
        gui.password_history.clear()

    def test_get_selected_password_returns_empty_when_no_valid_selection(self):
        gui.combobox_generated_password = MagicMock()
        gui.combobox_generated_password.current.return_value = -1
        self.assertEqual(gui.get_selected_password(), "")

    def test_get_selected_password_returns_selected_history_entry(self):
        gui.password_history.append({"password": "Ab3!xyZ9", "settings": make_settings()})
        gui.combobox_generated_password = MagicMock()
        gui.combobox_generated_password.current.return_value = 0
        self.assertEqual(gui.get_selected_password(), "Ab3!xyZ9")

    def test_get_settings_uses_selected_password_settings(self):
        saved_settings = make_settings()
        saved_settings["password_length"] = 10
        gui.password_history.append({"password": "Ab3!xyZ9xx", "settings": saved_settings})
        gui.combobox_generated_password = MagicMock()
        gui.combobox_generated_password.current.return_value = 0
        self.assertEqual(gui.get_settings_for_selected_password(), saved_settings)

    def test_get_settings_falls_back_to_current_options_without_selection(self):
        gui.combobox_generated_password = MagicMock()
        gui.combobox_generated_password.current.return_value = -1
        self.assertEqual(gui.get_settings_for_selected_password(), gui.password_option)

    def test_generate_password_records_password_and_settings_snapshot(self):
        gui.password_option.update(make_settings())
        with patch.object(gui, "random_password_generator", return_value="Ab3!xyZ9"):
            result = gui.generate_password()
        self.assertEqual(result, "Ab3!xyZ9")
        self.assertEqual(gui.password_history[-1]["password"], "Ab3!xyZ9")
        self.assertEqual(gui.password_history[-1]["settings"], make_settings())

    def test_saved_history_settings_are_not_same_mutable_dict(self):
        gui.password_option.update(make_settings())
        with patch.object(gui, "random_password_generator", return_value="Ab3!xyZ9"):
            gui.generate_password()
        gui.password_option["password_length"] = 20
        self.assertEqual(gui.password_history[-1]["settings"]["password_length"], 8)

    def test_set_password_length_rejects_invalid_length(self):
        gui.spinbox_password_length = MagicMock()
        gui.spinbox_password_length.get.return_value = "7"
        with self.assertRaises(ValueError):
            gui.set_password_length()

    def test_set_password_length_stores_valid_length(self):
        gui.spinbox_password_length = MagicMock()
        gui.spinbox_password_length.get.return_value = "15"
        gui.set_password_length()
        self.assertEqual(gui.password_option["password_length"], 15)

    @patch.object(gui.messagebox, "showinfo")
    def test_empty_password_copy_is_blocked(self, mock_showinfo):
        self.assertTrue(gui.show_copy_error_if_empty(""))
        mock_showinfo.assert_called_once()

    @patch.object(gui.messagebox, "showinfo")
    def test_empty_password_save_is_blocked(self, mock_showinfo):
        self.assertFalse(gui.show_save_error_if_empty(""))
        mock_showinfo.assert_called_once()

    def test_nonempty_password_can_be_saved(self):
        with patch.object(gui.messagebox, "showinfo") as mock_showinfo:
            self.assertTrue(gui.show_save_error_if_empty("Ab3!xyZ9"))
        mock_showinfo.assert_not_called()

    def test_reset_clears_history_and_display(self):
        gui.password_history.append({"password": "Ab3!xyZ9", "settings": make_settings()})
        gui.combobox_generated_password = MagicMock()
        gui.labels = {
            "label_entropy_value": MagicMock(),
            "label_show_strength": MagicMock(),
        }
        gui.progressbar_generated_password = MagicMock()
        gui.reset_password_ui()
        self.assertEqual(gui.password_history, [])
        gui.combobox_generated_password.set.assert_called_once_with("")
        gui.combobox_generated_password.config.assert_called_once_with(values=())
        gui.progressbar_generated_password.config.assert_called_once_with(value=0)

    def test_save_password_to_file_writes_password_history(self):
        gui.password_history.extend([
            {"password": "Ab3!xyZ9", "settings": make_settings()},
            {"password": "Cd4@uvW7", "settings": make_settings()},
        ])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "passwords.txt"
            with patch.object(gui, "asksaveasfilename", return_value=str(path)):
                with patch.object(gui.messagebox, "showinfo"):
                    gui.save_password_to_file()
            self.assertEqual(path.read_text(encoding="utf-8"), "Ab3!xyZ9\nCd4@uvW7")


if __name__ == "__main__":
    unittest.main()
