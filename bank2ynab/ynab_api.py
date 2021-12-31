import json
import logging
from configparser import DuplicateSectionError, NoSectionError

import requests

from config_handler import ConfigHandler
from ynab_api_response import YNABError

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

        self.user_config_handler = ConfigHandler(user_mode=True)
        self.user_config = self.user_config_handler.config
        self.user_config_path = self.user_config_handler.user_conf_path

        # TODO: Fix debug structure, so it will be used in logging instead
        self.debug = False

    def run(self, transaction_data: dict[str, str]):
        if self.api_token is not None:
            logging.info("Connecting to YNAB API...")
            logging.debug(transaction_data)
            # get the list of budgets
            budget_ids = list_budgets(api_token=self.api_token)
            # if there's only one budget, silently set a default budget
            if len(budget_ids) == 1:
                self.budget_id = budget_ids[0][1]

            budget_transactions = self.process_transactions(transaction_data)

            for budget in budget_ids:
                id = budget[1]
                try:
                    post_transactions(
                        api_token=self.api_token,
                        budget_id=id,
                        transaction_data=budget_transactions[id],
                    )
                except KeyError:
                    logging.info(f"No transactions to upload for {budget[0]}.")
        else:
            logging.info("No API-token provided.")

    def process_transactions(self, transaction_data: dict[str, str]) -> dict:
        """
        :param transaction_data: dict of bank names:combined transaction string
        :return budget_json_dict: dict of budget_ids:ready-to-post transactions
        """
        logging.info("Processing transactions...")
        budget_json_dict: dict[str, str] = dict()
        # get transactions for each bank
        for bank in transaction_data.keys():
            # get the budget ID and Account ID to write to
            budget_id, account_id = self.select_account(bank)
            account_transactions = transaction_data[bank]

            # insert account_id into each transaction
            account_transactions = account_transactions.replace(
                '"account_id":""', f'"account_id":"{account_id}"'
            )
            if budget_id in budget_json_dict:
                budget_json_dict[budget_id] += account_transactions
            else:
                budget_json_dict.setdefault(budget_id, account_transactions)

        return budget_json_dict

    def select_account(self, bank: str):
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
            instruction = "No YNAB {} for transactions from {} set!\nPick {}"
            # if no default budget, build budget list and select budget
            if self.budget_id is None:
                # msg =
                # "No YNAB budget for {} set! \nPick a budget".format(bank)
                msg = instruction.format("budget", bank, "a budget")
                budget_ids = list_budgets(api_token=self.api_token)
                budget_id = option_selection(budget_ids, msg)
            else:
                budget_id = self.budget_id

            # build account list and select account
            account_ids = list_accounts(
                api_token=self.api_token, budget_id=budget_id
            )
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
        # TODO move config saving to the ConfigHandler class?
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


def api_read(api_token: str, budget_id: str, keyword: str) -> dict:
    """
    General function for reading data from YNAB API.

    :param budget_id: ID of budget to access
    :type budget_id: str
    :param  keyword: keyword for data type, e.g. transactions
    :type keyword: str
    :raises YNABError: [description]
    :return: [description]
    :rtype: dict
    """
    base_url = "https://api.youneedabudget.com/v1/budgets/"

    if budget_id == "":
        # only happens when we're looking for the list of budgets
        url = base_url + f"?access_token={api_token}"
    else:
        url = base_url + f"{budget_id}/{keyword}?access_token={api_token}"

    response = requests.get(url)
    try:
        read_data = response.json()["data"][keyword]
    except KeyError:
        # the API has returned an error so let's handle it
        raise YNABError(response.json()["error"]["id"])
    return read_data


def list_accounts(api_token: str, budget_id: str) -> list[list[str]]:
    accounts = api_read(
        api_token=api_token, budget_id=budget_id, keyword="accounts"
    )

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


def list_budgets(api_token: str) -> list[str]:
    budgets = api_read(api_token=api_token, budget_id="", keyword="budgets")
    budget_ids = list()
    for budget in budgets:
        budget_ids.append([budget["name"], budget["id"]])
    return budget_ids


def post_transactions(
    api_token: str, budget_id: str, transaction_data: str
) -> None:
    # send our data to API

    logging.info("Uploading transactions to YNAB...")
    url = (
        "https://api.youneedabudget.com/v1/budgets/"
        + f"{budget_id}/transactions?access_token={api_token}"
    )
    data = "{data:{transactions:" + transaction_data + "} }"
    print(data)
    post_response = requests.post(url, json=data)
    json_data = json.loads(post_response.text)

    # response handling - TODO: make this more thorough!
    try:
        raise YNABError(json_data["error"]["id"])
    except KeyError:
        logging.info(
            f"Success: {len(json_data['data']['transaction_ids'])}"
            " entries uploaded,"
            f" {len(json_data['data']['duplicate_import_ids'])}"
            " entries skipped."
        )


def option_selection(options: list, msg: str) -> str:
    """
    Used to select from a list of options.
    If only one item in list, selects that by default.
    Otherwise displays "msg" asking for input selection (integer only).

    :param options: list of [name, option] pairs to select from
    :param msg: the message to display on the input line
    :return option_selected: the selected item from the list
    """
    print("\n")
    selection = 1
    count = len(options)
    if count > 1:
        for index, option in enumerate(options):
            print(f"| {index+1} | {option[0]}")
        selection = int_input(1, count, msg)
    option_selected = options[selection - 1][1]
    return option_selected


def int_input(min: int, max: int, msg: str) -> int:
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
