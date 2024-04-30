import importlib
import logging
from typing import Any

from .bank_handler import BankHandler
from .config_handler import ConfigHandler
from .ynab_api import YNAB_API

# configure our logger
logging.basicConfig(format="%(levelname): %(message)", level=logging.INFO)


def build_bank(bank_config: dict[str, Any]) -> BankHandler:
    """Factory method loading the correct class
    for a given configuration."""
    plugin_module_name = bank_config.get("plugin", None)
    if plugin_module_name:
        module = importlib.import_module(
            f".plugins.{plugin_module_name}", package="bank2ynab"
        )
        if not hasattr(module, "build_bank"):
            s = (
                f"The specified plugin {plugin_module_name}.py "
                "does not contain the required build_bank(config) method."
            )
            raise ImportError(s)
        bank = module.build_bank(bank_config)
        return bank
    else:
        return BankHandler(config_dict=bank_config)


def main():
    try:
        config_handler = ConfigHandler()
    except FileNotFoundError:
        logging.error("No configuration file found, process aborted.")
        pass
    else:
        # generate list of bank objects to process
        bank_obj_list: list[BankHandler] = []
        for bank_params in config_handler.config.sections():
            config_dict = config_handler.fix_conf_params(bank_params)
            # create bank object using config (allows for plugin use)
            bank_object = build_bank(bank_config=config_dict)
            bank_obj_list.append(bank_object)

        # initialize variables for summary:
        files_processed = 0
        bank_transaction_dict: dict[str, list] = dict()
        # process account for each config entry
        for bank_object in bank_obj_list:
            bank_object.run()
            if bank_object.transaction_list:
                bank_transaction_dict[bank_object.name] = (
                    bank_object.transaction_list
                )
            files_processed += bank_object.files_processed
        logging.info(
            f"\nFile processing complete! {files_processed} files processed.\n"
        )

        if bank_transaction_dict:
            api = YNAB_API(config_handler)
            api.run(bank_transaction_dict)


# Let's run this thing!
if __name__ == "__main__":
    main()
