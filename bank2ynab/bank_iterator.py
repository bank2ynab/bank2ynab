import importlib
import logging

from bank_handler import BankHandler
from config_handler import ConfigHandler

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


# Classes doing the actual work
class BankIterator:
    """Main program instance, responsible for gathering configuration,
    creating the right object for each bank, and triggering elaboration."""

    def __init__(self, config_handler: ConfigHandler):
        self.banks = []
        self.transaction_data = {}

        for section in config_handler.config.sections():
            config_dict = config_handler.fix_conf_params(section)
            bank_object = build_bank(bank_config=config_dict)
            self.banks.append(bank_object)

    def run(self):
        """Main program flow"""
        # initialize variables for summary:
        files_processed = 0
        # process account for each config file
        for bank in self.banks:
            bank_process = bank.run()
            # do something with bank_df so we can pass to API class
            """TODO API linkage!"""
            bank_process[1]
            files_processed += bank_process[0]

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
