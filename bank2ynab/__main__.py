import logging

from bank_iterator import BankIterator
from config_handler import ConfigHandler
from ynab_api import YNAB_API

# configure our logger
logging.basicConfig(format="%(levelname): %(message)", level=logging.INFO)

# Let's run this thing!
if __name__ == "__main__":
    try:
        config_handler = ConfigHandler()
    except FileNotFoundError:
        logging.error("No configuration file found, process aborted.")
        pass
    else:
        bank_iterator = BankIterator(config_handler)
        bank_iterator.run()
        if bank_iterator.bank_transaction_dict:
            api = YNAB_API(config_handler)
            api.run(bank_iterator.bank_transaction_dict)
