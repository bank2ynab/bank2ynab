import requests
import json
import configparser
import logging

import b2y_utilities

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


class YNAB_API(object):  # in progress (2)
    """
    uses Personal Access Token stored in user_configuration.conf
    (note for devs: be careful not to accidentally share API access token!)
    """

    def __init__(self, config_object, transactions=None):
        self.transactions = []
        self.budget_id = None
        self.config = b2y_utilities.get_configs()
        self.api_token = self.config.get("DEFAULT", "YNAB API Access Token")
        # TODO make user_config section play nice with
        # b2y_utilities.get_configs()
        self.user_config_path = "user_configuration.conf"
        self.user_config = configparser.RawConfigParser()

        # TODO: Fix debug structure, so it will be used in logging instead
        self.debug = False

    def run(self, transaction_data):
        if self.api_token is not None:
            logging.info("Connecting to YNAB API...")

            # check for API token auth (and other errors)
            error_code = self.list_budgets()
            if error_code[0] == "ERROR":
                return error_code
            else:
                # generate our list of budgets
                budget_ids = self.list_budgets()
                # if there's only one budget, silently set a default budget
                if len(budget_ids) == 1:
                    self.budget_id = budget_ids[0]

                budget_t_data = self.process_transactions(transaction_data)
                for budget in budget_ids:
                    id = budget[1]
                    try:
                        self.post_transactions(id, budget_t_data[id])
                    except KeyError:
                        logging.info(
                            "No transactions to upload for {}.".format(
                                budget[0]
                            )
                        )
        else:
            logging.info("No API-token provided.")

    def api_read(self, budget_id, kwd):
        """
        General function for reading data from YNAB API
        :param  budget: boolean indicating if there's a default budget
        :param  kwd: keyword for data type, e.g. transactions
        :return error_codes: if it fails we return our error
        """
        api_t = self.api_token
        base_url = "https://api.youneedabudget.com/v1/budgets/"

        if budget_id is None:
            # only happens when we're looking for the list of budgets
            url = base_url + "?access_token={}".format(api_t)
        else:
            url = base_url + "{}/{}?access_token={}".format(
                budget_id, kwd, api_t
            )

        response = requests.get(url)
        try:
            read_data = response.json()["data"][kwd]
        except KeyError:
            # the API has returned an error so let's handle it
            return self.process_api_response(response.json()["error"])
        return read_data

    def process_transactions(self, transaction_data):
        """
        :param transaction_data: dict of bank names to transaction lists
        :param transactions: list of individual transaction dictionaries
        :return budget_t_data: dict of budget_ids ready-to-post transactions
        """
        logging.info("Processing transactions...")
        # go through each bank's data
        budget_t_data = {}
        budget_transactions = []
        for bank in transaction_data:
            # what budget and account to write this bank's transactions to
            budget_id, account_id = self.select_account(bank)
            # save transaction data for each bank in main list
            account_transactions = transaction_data[bank]

            try:
                budget_transactions = budget_t_data[budget_id]["transactions"]
            except KeyError:
                budget_transactions = []
                budget_t_data[budget_id] = {"transactions": []}
            for t in account_transactions[1:]:
                trans_dict = self.create_transaction(
                    account_id, t, budget_transactions
                )
                budget_transactions.append(trans_dict)
            budget_t_data[budget_id]["transactions"] = budget_transactions
        return budget_t_data

    def create_transaction(self, account_id, this_trans, transactions):
        date = this_trans[0]
        payee = this_trans[1]
        category = this_trans[2]
        memo = this_trans[3]
        amount = b2y_utilities.string_num_diff(this_trans[4], this_trans[5])

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
            "flag_color": None,
        }
        return transaction

    def create_import_id(self, amount, date, existing_transactions):
        """
        Create import ID for our transaction
        import_id format = YNAB:amount:ISO-date:occurrences
        Maximum 36 characters ("YNAB" + ISO-date = 10 characters)
        :param amount: transaction amount in "milliunits"
        :param date: date in ISO format
        :param existing_transactions: list of currently-compiled transactions
        :return: properly formatted import ID
        """
        # check is there a duplicate transaction already
        count = 1
        for transaction in existing_transactions:
            try:
                if transaction["import_id"].startswith(
                    "YNAB:{}:{}:".format(amount, date)
                ):
                    count += 1
            except KeyError:
                # transaction doesn't have import id for some reason
                pass
        return "YNAB:{}:{}:{}".format(amount, date, count)

    def post_transactions(self, budget_id, data):
        # send our data to API
        logging.info("Uploading transactions to YNAB...")
        url = (
            "https://api.youneedabudget.com/v1/budgets/"
            + "{}/transactions?access_token={}".format(
                budget_id, self.api_token
            )
        )

        post_response = requests.post(url, json=data)

        # response handling - TODO: make this more thorough!
        try:
            self.process_api_response(json.loads(post_response.text)["error"])
        except KeyError:
            logging.info("Success!")

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

    def list_accounts(self, budget_id):
        accounts = self.api_read(budget_id, "accounts")
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

    def list_budgets(self):
        budgets = self.api_read(None, "budgets")
        if budgets[0] == "ERROR":
            return budgets

        budget_ids = list()
        for budget in budgets:
            budget_ids.append([budget["name"], budget["id"]])

            # commented out because this is a bit messy and confusing
            # TODO: make this legible!
            """
            # debug messages:
            for key, value in budget.items():
                if(type(value) is dict):
                    logging.debug("%s: " % str(key))
                    for subkey, subvalue in value.items():
                        logging.debug("  %s: %s" %
                                      (str(subkey), str(subvalue)))
                else:
                    logging.debug("%s: %s" % (str(key), str(value)))
            """
        return budget_ids

    def process_api_response(self, details):
        """
        Prints details about errors returned by the YNAB api
        :param details: dictionary of returned error info from the YNAB api
        :return id: HTTP error ID
        :return detail: human-understandable explanation of error
        """
        # TODO: make this function into a general response handler instead
        errors = {
            "400": "Bad syntax or validation error",
            "401": "API access token missing, invalid, revoked, or expired",
            "403.1": "The subscription for this account has lapsed.",
            "403.2": "The trial for this account has expired.",
            "404.1": "The specified URI does not exist.",
            "404.2": "Resource not found",
            "409": "Conflict error",
            "429": "Too many requests. Wait a while and try again.",
            "500": "Unexpected error",
        }
        id = details["id"]
        name = details["name"]
        detail = errors[id]
        logging.error("{} - {} ({})".format(id, detail, name))

        return ["ERROR", id, detail]

    def select_account(self, bank):
        account_id = ""
        # check if bank has account associated with it already
        try:
            config_line = b2y_utilities.get_config_line(
                self.config, bank, ["YNAB Account ID", False, "||"]
            )
            budget_id = config_line[0]
            account_id = config_line[1]
            logging.info("Previously-saved account for {} found.".format(bank))
        except IndexError:
            pass
        except configparser.NoSectionError:
            logging.info("No user configuration for {} found.".format(bank))

        if account_id == "":
            instruction = "No YNAB {} for transactions from {} set!\n Pick {}"
            # if no default budget, build budget list and select budget
            if self.budget_id is None:
                # msg =
                # "No YNAB budget for {} set! \nPick a budget".format(bank)
                msg = instruction.format("budget", bank, "a budget")
                budget_ids = self.list_budgets()
                budget_id = b2y_utilities.option_selection(budget_ids, msg)
            else:
                budget_id = self.budget_id

            # build account list and select account
            account_ids = self.list_accounts(budget_id)
            # msg = "Pick a YNAB account for transactions from {}".format(bank)
            msg = instruction.format("account", bank, "an account")
            account_id = b2y_utilities.option_selection(account_ids, msg)
            # save account selection for bank
            self.save_account_selection(bank, budget_id, account_id)
        return budget_id, account_id

    def save_account_selection(self, bank, budget_id, account_id):
        """
        saves YNAB account to use for each bank
        """
        self.user_config.read(self.user_config_path)
        try:
            self.user_config.add_section(bank)
        except configparser.DuplicateSectionError:
            pass
        self.user_config.set(
            bank, "YNAB Account ID", "{}||{}".format(budget_id, account_id)
        )

        logging.info("Saving default account for {}...".format(bank))
        with open(self.user_config_path, "w", encoding="utf-8") as config_file:
            self.user_config.write(config_file)
