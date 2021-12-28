import importlib
import logging

from bank_handler import BankHandler
from config_handler import ConfigHandler

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


class BankIterator:
    """Main program instance, responsible for gathering configuration,
    creating the right object for each bank, and triggering elaboration."""

    def __init__(self, config_handler: ConfigHandler):
        self.banks = []
        self.transaction_data = []

        for section in config_handler.config.sections():
            config_dict = config_handler.fix_conf_params(section)
            bank_object = build_bank(bank_config=config_dict)
            self.banks.append(bank_object)

    def run(self):
        """Main program flow"""
        # initialize variables for summary:
        files_processed = 0
        # process account for each config file
        for bank_object in self.banks:
            bank_object.run()
            if bank_object.transaction_data:
                self.transaction_data.append(bank_object.transaction_data)
            files_processed += bank_object.bank_files_processed

        logging.info(f"\nDone! {files_processed} files processed.\n")


def build_bank(bank_config: dict) -> BankHandler:
    """Factory method loading the correct class
    for a given configuration."""
    plugin_module_name = bank_config.get("plugin", None)
    if plugin_module_name:
        module = importlib.import_module(f"plugins.{plugin_module_name}")
        if not hasattr(module, "build_bank"):
            s = (
                f"The specified plugin {plugin_module_name}.py"
                + "does not contain the required "
                "build_bank(config) method."
            )
            raise ImportError(s)
        bank = module.build_bank(bank_config)
        return bank
    else:
        return BankHandler(config_dict=bank_config)
