import json
import logging
from configparser import DuplicateSectionError, NoSectionError

import requests

from config_handler import ConfigHandler

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


class YNAB_API:
    # TODO - revise docstring
    # TODO - break up class - too many responsibilities
    #           - ??? what subsets to use
    # TODO - create API Error class?
    # TODO - handle transaction creation in DataframeCleaner?
    """
    uses Personal Access Token stored in user_configuration.conf
    (note for devs: be careful not to accidentally share API access token!)
    """

    def __init__(
        self, config_object: ConfigHandler, transactions=None
    ) -> None:
        self.transactions = []
        self.budget_id = None
        self.config_handler = config_object
        self.api_token = self.config_handler.config.get(
            "DEFAULT", "YNAB API Access Token"
        )
        # self.api_token = 0  # debug - TODO remove line
        self.user_config_handler = ConfigHandler(user_mode=True)
        self.user_config = self.user_config_handler.config
        self.user_config_path = self.user_config_handler.user_conf_path

        # TODO: Fix debug structure, so it will be used in logging instead
        self.debug = False

    def run(self, transaction_data):
        if self.api_token is not None:
            logging.info("Connecting to YNAB API...")
            logging.debug(transaction_data)
            # check for API token auth (and other errors)
            error_code = self.list_budgets()
            if error_code[0] == "ERROR":
                return error_code
            else:
                # generate our list of budgets
                budget_ids = self.list_budgets()
                # if there's only one budget, silently set a default budget
                if len(budget_ids) == 1:
                    self.budget_id = budget_ids[0][1]

                budget_t_data = self.process_transactions(transaction_data)
                for budget in budget_ids:
                    id = budget[1]
                    try:
                        self.post_transactions(id, budget_t_data[id])
                    except KeyError:
                        logging.info(
                            "No transactions to upload for {budget[0]}."
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
            url = base_url + f"?access_token={api_t}"
        else:
            url = base_url + f"{budget_id}/{kwd}?access_token={api_t}"

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
        raise NotImplementedError
        """ logging.info("Processing transactions...")
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
        return budget_t_data """

    def post_transactions(self, budget_id, data):
        # send our data to API
        logging.info("Uploading transactions to YNAB...")
        url = (
            "https://api.youneedabudget.com/v1/budgets/"
            + f"{budget_id}/transactions?access_token={self.api_token}"
        )

        post_response = requests.post(url, json=data)
        json_data = json.loads(post_response.text)

        # response handling - TODO: make this more thorough!
        try:
            self.process_api_response(json_data["error"])
        except KeyError:
            logging.info(
                "Success: {} entries uploaded, {} entries skipped.".format(
                    len(json_data["data"]["transaction_ids"]),
                    len(json_data["data"]["duplicate_import_ids"]),
                )
            )

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
                logging.debug(f"id: {account['id']}")
                logging.debug(f"on_budget: {account['on_budget']}")
                logging.debug(f"closed: {account['closed']}")
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
        logging.error(f"{id} - {detail} ({name})")

        return ["ERROR", id, detail]

    def select_account(self, bank):
        account_id = ""
        budget_id = ""
        # check if bank has account associated with it already
        try:
            config_line = self.config_handler.get_config_line_lst(
                bank, "YNAB Account ID", "||"
            )
            budget_id = config_line[0]
            account_id = config_line[1]
            logging.info(f"Previously-saved account for {bank} found.")
        except IndexError:
            pass
        except NoSectionError:
            # TODO - can we handle this within the config class?
            logging.info(f"No user configuration for {bank} found.")

        if account_id == "":
            instruction = "No YNAB {} for transactions from {} set!\n Pick {}"
            # if no default budget, build budget list and select budget
            if self.budget_id is None:
                # msg =
                # "No YNAB budget for {} set! \nPick a budget".format(bank)
                msg = instruction.format("budget", bank, "a budget")
                budget_ids = self.list_budgets()
                budget_id = option_selection(budget_ids, msg)
            else:
                budget_id = self.budget_id

            # build account list and select account
            account_ids = self.list_accounts(budget_id)
            # msg = "Pick a YNAB account for transactions from {}".format(bank)
            msg = instruction.format("account", bank, "an account")
            account_id = option_selection(account_ids, msg)
            # save account selection for bank
            save_ac_toggle = self.config_handler.get_config_line_boo(
                bank, "Save YNAB Account"
            )
            if save_ac_toggle is True:
                self.save_account_selection(bank, budget_id, account_id)
            else:
                logging.info(
                    f"Saving default YNAB account is disabled for {bank}"
                    + " - account match not saved."
                )
        return budget_id, account_id

    def save_account_selection(self, bank, budget_id, account_id):
        # TODO move config saving to the ConfigHandler class
        """
        saves YNAB account to use for each bank
        """
        self.user_config.read(self.user_config_path)
        try:
            self.user_config.add_section(bank)
        except DuplicateSectionError:
            pass
        self.user_config.set(
            bank, "YNAB Account ID", f"{budget_id}||{account_id}"
        )

        logging.info(f"Saving default account for {bank}...")
        with open(self.user_config_path, "w", encoding="utf-8") as config_file:
            self.user_config.write(config_file)


def option_selection(options, msg):
    """
    Used to select from a list of options
    If only one item in list, selects that by default
    Otherwise displays "msg" asking for input selection (integer only)
    :param options: list of [name, option] pairs to select from
    :param msg: the message to display on the input line
    :return option_selected: the selected item from the list
    """
    selection = 1
    count = len(options)
    if count > 1:
        index = 0
        for option in options:
            index += 1
            print(f"| {index} | {option[0]}")
        selection = int_input(1, count, msg)
    option_selected = options[selection - 1][1]
    return option_selected


def int_input(min, max, msg):
    """
    Makes a user select an integer between min & max stated values
    :param  min: the minimum acceptable integer value
    :param  max: the maximum acceptable integer value
    :param  msg: the message to display on the input line
    :return user_input: sanitised integer input in acceptable range
    """
    while True:
        try:
            user_input = int(input(f"{msg} (range {min} - {max}): "))
            if user_input not in range(min, max + 1):
                raise ValueError
            break
        except ValueError:
            logging.info(
                "This integer is not in the acceptable range, try again!"
            )
    return user_input
