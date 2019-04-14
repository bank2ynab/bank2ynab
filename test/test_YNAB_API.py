"""from copy import copy"""

from test.utils import get_test_confparser
from unittest import TestCase

from os.path import join  # , abspath, exists

"""
import os

from bank2ynab import (B2YBank, fix_conf_params, build_bank, option_selection,
    int_input, string_num_diff
"""


_PY2 = False


class Test_YNAB_API(TestCase):

    TESTCONFPATH = join("test-data", "test.conf")

    def setUp(self):
        global _PY2
        self.cp, self.py2, = get_test_confparser()
        self.defaults = dict(self.cp.defaults())
        self.b = None

    def tearDown(self):
        pass

    def test_init_and_name(self):
        """ Check parameters are correctly stored in the object.
        self.b = B2YBank(self.defaults, self.py2)
        cfe = copy(self.defaults)
        self.assertEqual(self.b.config, cfe)
        self.assertEqual("DEFAULT", self.b.name)

        def __init__(self, config_object, transactions=None):
        self.transactions = []
        self.account_ids = []
        # TODO - make this play nice with our get_configs method (PY2)
        self.config = configparser.RawConfigParser()
        self.config.read("user_configuration.conf")
        self.api_token = self.config.get("DEFAULT", "YNAB API Access Token")
        self.budget_id = None

        # TODO: Fix debug structure, so it will be used in logging instead
        self.debug = False
        """

    def test_run(self):
        """
        def run(self, transaction_data):
        if(self.api_token is not None):
            logging.info("Connecting to YNAB API...")

            # check for API token auth (and other errors)
            error_code = self.list_budgets()
            if error_code[0] == "ERROR":
                return error_code
            else:
                # if no default budget, build budget list and select default
                if self.budget_id is None:
                    msg = "No default budget set! \nPick a budget"
                    budget_ids = self.list_budgets()
                    self.budget_id = option_selection(budget_ids, msg)

                transactions = self.process_transactions(transaction_data)
                if transactions["transactions"] != []:
                    self.post_transactions(transactions)
        else:
            logging.info("No API-token provided.")
        """

    def test_api_read(self):
        """
        def api_read(self, budget, kwd):

       General function for reading data from YNAB API
       :param  budget: boolean indicating if there's a default budget
       :param  kwd: keyword for data type, e.g. transactions
       :return error_codes: if it fails we return our error

        id = self.budget_id
        api_t = self.api_token
        base_url = "https://api.youneedabudget.com/v1/budgets/"

        if budget is False:
            # only happens when we're looking for the list of budgets
            url = base_url + "?access_token={}".format(api_t)
        else:
            url = base_url + "{}/{}?access_token={}".format(id, kwd, api_t)

        response = requests.get(url)
        try:
            read_data = response.json()["data"][kwd]
        except KeyError:
            # the API has returned an error so let's handle it
            return self.process_api_response(response.json()["error"])
        return read_data
        """

    def test_process_transactions(self):
        """
        :param transaction_data: dictionary of bank names to transaction lists

        logging.info("Processing transactions...")
        # go through each bank's data
        transactions = []
        for bank in transaction_data:
            # choose what account to write this bank's transactions to
            account_id = self.select_account(bank)
            # save transaction data for each bank in main dict
            account_transactions = transaction_data[bank]
            for t in account_transactions[1:]:
                trans_dict = self.create_transaction(
                    account_id, t, transactions)
                transactions.append(trans_dict)
        # compile our data to post
        data = {
            "transactions": transactions
        }
        return data
        """

    def test_create_transaction(self):
        """
        (self, account_id, this_trans, transactions):
        date = this_trans[0]
        payee = this_trans[1]
        category = this_trans[2]
        memo = this_trans[3]
        amount = string_num_diff(this_trans[4], this_trans[5])

        # assign values to transaction dictionary
        transaction = {
            "account_id": account_id,
            "date": date,
            "payee_name": payee[:50],
            "amount": amount,
            "memo": memo[:100],
            "category": category,
            "cleared": "cleared",
            "import_id": self.create_import_id(amount, date, transactions),
            "payee_id": None,
            "category_id": None,
            "approved": False,
            "flag_color": None
        }
        return transaction
        """

    def test_create_import_id(self):
        """
        def create_import_id(self, amount, date, existing_transactions):
        Create import ID for our transaction
        import_id format = YNAB:amount:ISO-date:occurrences
        Maximum 36 characters ("YNAB" + ISO-date = 10 characters)
        :param amount: transaction amount in "milliunits"
        :param date: date in ISO format
        :param existing_transactions: list of currently-compiled transactions
        :return: properly formatted import ID

        # check is there a duplicate transaction already
        count = 1
        for transaction in existing_transactions:
            if transaction["import_id"].startswith(
                    "YNAB:{}:{}:".format(amount, date)):
                count += 1
        return "YNAB:{}:{}:{}".format(amount, date, count)
        """

    def test_post_transactions(self):
        """
        def post_transactions(self, data):
            # send our data to API
            logging.info("Uploading transactions to YNAB...")
            url = ("https://api.youneedabudget.com/v1/budgets/" +
                   "{}/transactions?access_token={}".format(
                       self.budget_id,
                       self.api_token))

            post_response = requests.post(url, json=data)

            # response handling - TODO: make this more thorough!
            try:
                self.process_api_response(json.loads(post_response.text)["error"])
            except KeyError:
                logging.info("Success!")
        """

    def test_list_transactions(self):
        """
        def list_transactions(self):
            transactions = self.api_read(True, "transactions")
            if transactions[0] == "ERROR":
                return transactions

            if len(transactions) > 0:
                logging.debug("Listing transactions:")
                for t in transactions:
                    logging.debug(t)
            else:
                logging.debug("no transactions found")
        """

    def test_list_accounts(self):
        """
        def list_accounts(self):
            accounts = self.api_read(True, "accounts")
            if accounts[0] == "ERROR":
                return accounts

            account_ids = list()
            if len(accounts) > 0:
                for account in accounts:
                    account_ids.append([account["name"], account["id"]])
                    # debug messages
                    logging.debug("id: {}".format(account["id"]))
                    logging.debug("on_budget: {}".format(account["on_budget"]))
                    logging.debug("closed: {}".format(account["closed"]))
            else:
                logging.info("no accounts found")

            return account_ids
        """

    def test_list_budgets(self):
        """
        def list_budgets(self):
            budgets = self.api_read(False, "budgets")
            if budgets[0] == "ERROR":
                return budgets

            budget_ids = list()
            for budget in budgets:
                budget_ids.append([budget["name"], budget["id"]])

                commented out because this is a bit messy and confusing
                # TODO: make this legible!
                # debug messages:
                #for key, value in budget.items():
                    if(type(value) is dict):
                        logging.debug("%s: " % str(key))
                        for subkey, subvalue in value.items():
                            logging.debug("  %s: %s" %
                                         (str(subkey), str(subvalue)))
                    else:
                        logging.debug("%s: %s" % (str(key), str(value)))

            return budget_ids
        """

    def test_process_api_response(self):
        """
        def process_api_response(self, details):

            Prints details about errors returned by the YNAB api
            :param details: dictionary of returned error info from the YNAB api
            :return id: HTTP error ID
            :return detail: human-understandable explanation of error

            # TODO: make this function into a general response handler instead
            errors = {
                "400": "Bad syntax or validation error",
                "401": "API access token missing, invalid,
                revoked, or expired",
                "403.1": "The subscription for this account has lapsed.",
                "403.2": "The trial for this account has expired.",
                "404.1": "The specified URI does not exist.",
                "404.2": "Resource not found",
                "409": "Conflict error",
                "429": "Too many requests. Wait a while and try again.",
                "500": "Unexpected error"
            }
            id = details["id"]
            name = details["name"]
            detail = errors[id]
            logging.error("{} - {} ({})".format(id, detail, name))

            return ["ERROR", id, detail]
        """

    def test_select_account(self):
        """
        def select_account(self, bank):
            account_id = ""
            # check if bank has account associated with it already
            try:
                config_line = get_config_line(
                    self.config, bank, ["YNAB Account ID", False, "|"])
                # make sure the budget ID matches
                if config_line[0] == self.budget_id:
                    account_id = config_line[1]
                    logging.info(
                        "Previously-saved account for {} found.".format(bank))
                else:
                    raise configparser.NoSectionError
            except configparser.NoSectionError:
                logging.info("No user configuration for {} found.".format(
                    bank))
            if account_id == "":
                account_ids = self.list_accounts()
                # create list of account_ids
                msg = "Pick a YNAB account for transactions
                    from {}".format(bank)
                account_id = option_selection(account_ids, msg)
                # save account selection for bank
                self.save_account_selection(bank, account_id)
            return account_id
        """

    def test_save_account_selection(self):
        """
        def save_account_selection(self, bank, account_id):

            saves YNAB account to use for each bank

            try:
                self.config.add_section(bank)
            except configparser.DuplicateSectionError:
                pass
            self.config.set(bank, "YNAB Account ID",
                            "{}||{}".format(self.budget_id, account_id))

            logging.info("Saving default account for {}...".format(bank))
            with open("user_configuration.conf", "w") as config_file:
                self.config.write(config_file)
        """
