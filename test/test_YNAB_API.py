from test.utils import get_test_confparser
from unittest import TestCase

from os.path import join
import os
from shutil import copyfile
from bank2ynab import YNAB_API
import configparser
_PY2 = False


class Test_YNAB_API(TestCase):

    def setUp(self):
        global _PY2
        self.TESTCONFPATH = join("test-data", "test.conf")
        self.TEMPCONFPATH = join("test-data", "temp-test.conf")
        self.cp, self.py2, = get_test_confparser()
        self.defaults = dict(self.cp.defaults())
        self.test_class = None
        # copy config file to temp location
        copyfile(self.TESTCONFPATH, self.TEMPCONFPATH)

    def tearDown(self):
        # restore config file from temp location
        if os.path.exists(self.TEMPCONFPATH):
            os.remove(self.TEMPCONFPATH)
            pass

    def test_init_and_name(self):  # todo
        """ Check parameters are correctly stored in the API object."""
        """
        self.test_class = YNAB_API(self.defaults)
        cfe = copy(self.defaults)
        self.assertEqual(self.test_class.config, cfe)
        self.assertEqual("DEFAULT", self.test_class.name)
        """
        """
        def __init__(self, config_object, transactions=None):
        self.transactions = []
        self.account_ids = []
        self.config = configparser.RawConfigParser()
        self.config.read("user_configuration.conf")
        self.api_token = self.config.get("DEFAULT", "YNAB API Access Token")
        self.budget_id = None
        """

    def test_run(self):  # todo
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

    def test_api_read(self):  # todo
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

    def test_process_transactions(self):  # todo
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

    def test_create_transaction(self):  # todo
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

    def test_create_import_id(self):  # todo
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

    def test_post_transactions(self):  # todo
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

    def test_list_transactions(self):  # todo
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

    def test_list_accounts(self):  # todo
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

    def test_list_budgets(self):  # todo
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
                # for key, value in budget.items():
                    if(type(value) is dict):
                        logging.debug("%s: " % str(key))
                        for subkey, subvalue in value.items():
                            logging.debug("  %s: %s" %
                                         (str(subkey), str(subvalue)))
                    else:
                        logging.debug("%s: %s" % (str(key), str(value)))

            return budget_ids
        """

    def test_process_api_response(self):  # todo
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

    # IN PROGRESS
    # TODO - mock list_accounts & option_selection
    def test_select_account(self):
        """
        Test account selection logic
        """
        test_class = YNAB_API(self.cp)
        test_class.budget_id = "Test Budget ID"
        test_banks = [
            ("test_api_existing_bank", "Test Account ID"),
            ("New Bank", "Account 2")
        ]
        test_class.config_path = self.TEMPCONFPATH
        test_class.config = configparser.RawConfigParser()
        test_class.config.read(test_class.config_path)

        for bank, target_id in test_banks:
            id = test_class.select_account(bank)
            print("\nbank: {} || id: {} || target_id: {}\n".format(
                bank, id, target_id))  # debugging account selection!
            self.assertEqual(id, target_id)

    def test_save_account_selection(self):
        """
        Test that account info is saved under the correct bank and
        in the correct file.
        """
        test_class = YNAB_API(self.cp)
        test_class.budget_id = "Test Budget ID"
        test_account_id = "Test Account ID"
        test_banks = ["New Bank", "Existing Bank"]
        test_class.config_path = self.TEMPCONFPATH
        test_class.config = configparser.RawConfigParser()
        test_class.config.read(test_class.config_path)

        # save test bank details to test config
        for test_bank in test_banks:
            test_class.save_account_selection(test_bank, test_account_id)
        # check test config for test bank details & make sure ID matches
        config = configparser.RawConfigParser()
        config.read(test_class.config_path)
        for test_bank in test_banks:
            test_id = config.get(test_bank, "YNAB Account ID")
            self.assertEqual(test_id, "{}||{}".format(
                test_class.budget_id, test_account_id))
