import logging

from bank_process import Bank2Ynab
from b2y_utilities import get_configs
from ynab_api import YNAB_API

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

# Let's run this thing!
if __name__ == "__main__":
    try:
        config = get_configs()
    except FileNotFoundError:
        logging.error("No configuration file found, process aborted.")
        pass
    else:
        b2y = Bank2Ynab(config)
        b2y.run()
        api = YNAB_API(config)
        if b2y.transaction_data:
            api.run(b2y.transaction_data)
