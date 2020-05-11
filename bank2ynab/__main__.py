import logging

import b2y_utilities
import ynab_api

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

# Let's run this thing!
if __name__ == "__main__":
    try:
        config = b2y_utilities.get_configs()
    except FileNotFoundError:
        logging.error("No configuration file found, process aborted.")
        pass
    else:
        b2y = Bank2Ynab(config)
        b2y.run()
        api = YNAB_API(config)
        if b2y.transaction_data:
            api.run(b2y.transaction_data)
