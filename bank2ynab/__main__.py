#!/usr/bin/env python3
#
# bank2ynab.py
#
# Searches specified folder or default download folder for exported
# bank transaction file (.csv format) & adjusts format for YNAB import
# Please see here for details: https://github.com/torbengb/bank2ynab
#
# MIT License: https://github.com/torbengb/bank2ynab/blob/master/LICENSE
#
# DISCLAIMER: Please use at your own risk. This tool is neither officially
# supported by YNAB (the company) nor by YNAB (the software) in any way.
# Use of this tool could introduce problems into your budget that YNAB,
# through its official support channels, will not be able to troubleshoot
# or fix. See also the full MIT licence.

import logging

from bank_iterator import BankIterator
from config_handler import ConfigHandler
from ynab_api import YNAB_API

# configure our logger
logging.basicConfig(format=f"%(levelname): %(message)", level=logging.INFO)

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
        api = YNAB_API(config_handler)
        """ if bank_iterator.transaction_data: # DEBUG - disabled while testing
            api.run(bank_iterator.transaction_data) """
