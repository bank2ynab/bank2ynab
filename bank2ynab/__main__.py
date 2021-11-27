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

from b2y_utilities import get_configs
from BankIterator import BankIterator
from ynab_api import YNAB_API

# configure our logger
logging.basicConfig(format=f"%(levelname): %(message)", level=logging.INFO)

# Let's run this thing!
if __name__ == "__main__":
    try:
        config = get_configs()
    except FileNotFoundError:
        logging.error("No configuration file found, process aborted.")
        pass
    else:
        b2y = BankIterator(config)
        b2y.run()
        # api = YNAB_API(config) # DEBUG: disabled
        """ if b2y.transaction_data: # DEBUG - disabled while testing
            api.run(b2y.transaction_data) """
