import importlib
import logging

import b2y_utilities
from BankHandler import BankHandler

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


# Classes doing the actual work
class BankIterator:
    """Main program instance, responsible for gathering configuration,
    creating the right object for each bank, and triggering elaboration."""

    def __init__(self, config_object):
        self.banks = []
        self.transaction_data = {}

        for section in config_object.sections():
            bank_config = b2y_utilities.fix_conf_params(config_object, section)
            bank_object = self.build_bank(bank_config)
            self.banks.append(bank_object)

    def build_bank(self, bank_config):
        # TODO mostly commented out for now as plugins need to be fixed
        """Factory method loading the correct class for a given configuration."""
        plugin_module = bank_config.get("plugin", None)
        """ if plugin_module:
            p_mod = importlib.import_module("plugins.{}".format(plugin_module))
            if not hasattr(p_mod, "build_bank"):
                s = (
                    "The specified plugin {}.py".format(plugin_module)
                    + "does not contain the required "
                    "build_bank(config) method."
                )
                raise ImportError(s)
            bank = p_mod.build_bank(bank_config)
            return bank
            else: """  # DEBUG - plugins broken
        return BankHandler(bank_config)

    def run(self):
        """Main program flow"""
        # initialize variables for summary:
        files_processed = 0
        # process account for each config file
        for bank in self.banks:
            bank_files_processed, bank_df = bank.run()
            # do something with bank_df so we can pass to API class
            # TODO something!
            files_processed += bank_files_processed

        logging.info("\nDone! {} files processed.\n".format(files_processed))
