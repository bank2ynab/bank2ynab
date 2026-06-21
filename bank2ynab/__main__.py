import logging

from .bank_handler import BankHandler, build_bank
from .config_handler import ConfigHandler
from .ynab_api import YNAB_API

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)


class Bank2YNABApp:
    """Top-level application class that wires together config, banks, and API.

    Accepts an optional pre-built ConfigHandler for testing; constructs one
    from the default config files otherwise.
    """

    def __init__(self, config_handler: ConfigHandler | None = None) -> None:
        """Initialise the application.

        Args:
            config_handler: Optional pre-built ConfigHandler. If omitted,
                one is constructed from the default config files.

        Raises:
            FileNotFoundError: If no configuration file can be found.
        """
        self.config_handler = config_handler or ConfigHandler()
        logging.getLogger().setLevel(self.config_handler.get_log_level())

    def _build_banks(self) -> list[BankHandler]:
        """Build a BankHandler (or plugin subclass) for every config section.

        Returns:
            list[BankHandler]: One handler per configured bank format.
        """
        return [
            build_bank(bank_config=self.config_handler.fix_conf_params(section))
            for section in self.config_handler.config.sections()
        ]

    def _process_banks(self, bank_obj_list: list[BankHandler]) -> tuple[int, dict[str, list]]:
        """Run each bank handler and collect transaction data.

        Args:
            bank_obj_list: List of bank handlers to process.

        Returns:
            tuple[int, dict[str, list]]: Total files processed and a mapping
                of bank name to transaction records.
        """
        files_processed = 0
        bank_transaction_dict: dict[str, list] = {}
        for bank_object in bank_obj_list:
            bank_object.run()
            if bank_object.transaction_list:
                bank_transaction_dict[bank_object.name] = bank_object.transaction_list
            files_processed += bank_object.files_processed
        logging.info(f"\nFile processing complete! {files_processed} files processed.\n")
        return files_processed, bank_transaction_dict

    def run(self) -> None:
        """Execute the full bank-to-YNAB pipeline."""
        bank_obj_list = self._build_banks()
        _, bank_transaction_dict = self._process_banks(bank_obj_list)

        if bank_transaction_dict:
            try:
                api = YNAB_API(self.config_handler)
                api.run(bank_transaction_dict)
            except ValueError as e:
                logging.error(f"{e}")


def main() -> None:
    try:
        app = Bank2YNABApp()
    except FileNotFoundError:
        logging.error("No configuration file found, process aborted.")
        return
    app.run()


# Let's run this thing!
if __name__ == "__main__":
    main()
