import os
import tempfile
import unittest
from pathlib import Path

from bank2ynab.config_handler import ConfigHandler


class TestConfigHandlerPaths(unittest.TestCase):
    def setUp(self) -> None:
        self.prev_config_dir = os.environ.get("BANK2YNAB_CONFIG_DIR")

    def tearDown(self) -> None:
        if self.prev_config_dir is None:
            os.environ.pop("BANK2YNAB_CONFIG_DIR", None)
        else:
            os.environ["BANK2YNAB_CONFIG_DIR"] = self.prev_config_dir

    def test_packaged_defaults_are_copied_to_user_config_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_config:
            os.environ["BANK2YNAB_CONFIG_DIR"] = temp_config

            handler = ConfigHandler()

            bank_conf = Path(temp_config) / "bank2ynab.conf"
            user_conf = Path(temp_config) / "user_configuration.conf"
            self.assertEqual(Path(handler.bank_conf_path), bank_conf)
            self.assertEqual(Path(handler.user_conf_path), user_conf)
            self.assertTrue(bank_conf.exists())
            self.assertTrue(user_conf.exists())

    def test_payee_mappings_excludes_default_section_keys(self) -> None:
        """DEFAULT section keys must not bleed into payee_mappings."""
        with tempfile.TemporaryDirectory() as temp_config:
            os.environ["BANK2YNAB_CONFIG_DIR"] = temp_config

            # Let ConfigHandler seed bank2ynab.conf (supplies all DEFAULT values),
            # then append a test bank + its payee_mappings to the user conf.
            handler = ConfigHandler()
            user_conf = Path(handler.user_conf_path)
            user_conf.write_text(
                "[Test Bank]\n"
                "\n"
                "[Test Bank payee_mappings]\n"
                "PAYPAL = PayPal\n"
                "AMAZON = Amazon\n",
                encoding="utf-8",
            )
            handler = ConfigHandler()
            config = handler.fix_conf_params("Test Bank")

        self.assertEqual(config.payee_mappings, {"paypal": "PayPal", "amazon": "Amazon"})
        for default_key in handler.config.defaults():
            self.assertNotIn(default_key, config.payee_mappings)


if __name__ == "__main__":
    unittest.main()
