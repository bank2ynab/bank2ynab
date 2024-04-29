import logging
from configparser import DuplicateSectionError, NoSectionError

from . import api_interface
from . import user_input
from .api_interface import APIInterface
from .config_handler import ConfigHandler

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


class YNAB_API:
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

    def run(self, transaction_data: dict[str, list]):
        logging.debug(f"Transaction data: {transaction_data}")

        # get previously-saved budget/account mapping
        bank_account_mapping = self.get_saved_accounts(transaction_data)
        # load budget & account data from API
        api_connect = APIInterface(api_token=self.api_token)
        budget_info = api_connect.budget_info
        # remove any account IDs that don't exist in API info
        bank_account_mapping = remove_invalid_accounts(
            prev_saved_map=bank_account_mapping, api_data=budget_info
        )
        # ask user to set budget & account for each unsaved bank
        select_accounts(mappings=bank_account_mapping, budget_info=budget_info)
        # save account mappings
        self.save_account_mappings(bank_account_mapping)
        # map transactions to budget and account IDs
        budget_transactions = apply_mapping(
            transaction_data, bank_account_mapping
        )

        for budget_id in budget_info:
            try:
                api_interface.post_transactions(
                    api_token=self.api_token,
                    budget_id=budget_id,
                    data=budget_transactions[budget_id],
                )
            except KeyError:
                logging.info(
                    "No transactions to upload for"
                    f" {budget_info[budget_id]['name']}."
                )

    def get_saved_accounts(self, t_data: dict) -> dict[str, dict[str, str]]:
        bank_account_mapping = dict()
        for bank_name in t_data.keys():
            account_id = ""
            budget_id = ""
            # check if bank has account associated with it already
            try:
                config_line = self.config_handler.get_config_line_lst(
                    bank_name, "YNAB Account ID", "||"
                )
                budget_id = config_line[0]
                account_id = config_line[1]
                logging.info(
                    f"Previously-saved account for {bank_name} found."
                )
            except IndexError:
                pass
            except NoSectionError:
                # TODO - can we handle this within the config class?
                logging.info(f"No user configuration for {bank_name} found.")
            bank_account_mapping.setdefault(
                bank_name, {"account_id": account_id, "budget_id": budget_id}
            )
        return bank_account_mapping

    def save_account_mappings(self, mapping: dict[str, dict]):
        for bank_name in mapping:
            # save account selection for bank
            save_ac_toggle = self.config_handler.get_config_line_boo(
                bank_name, "Save YNAB Account"
            )
            if save_ac_toggle is True:
                self.save_account_selection(
                    bank_name,
                    mapping[bank_name]["budget_id"],
                    mapping[bank_name]["account_id"],
                )
            else:
                logging.info(
                    f"Saving default YNAB account is disabled for {bank_name}"
                    " - account match not saved."
                )

    def save_account_selection(self, bank, budget_id, account_id):
        # TODO move config saving to the ConfigHandler class?
        """
        saves YNAB account to use for each bank
        """
        self.user_config.read(self.user_config_path)
        try:
            self.user_config.add_section(bank)
            logging.info(f"Saving default account for {bank}...")
        except DuplicateSectionError:
            pass
        self.user_config.set(
            bank, "YNAB Account ID", f"{budget_id}||{account_id}"
        )

        with open(self.user_config_path, "w", encoding="utf-8") as config_file:
            self.user_config.write(config_file)


def remove_invalid_accounts(
    prev_saved_map: dict[str, dict[str, str]], api_data: dict[str, dict]
) -> dict[str, dict[str, str]]:
    temp_mapping = prev_saved_map
    for bank in prev_saved_map:
        budget_id = prev_saved_map[bank]["budget_id"]
        account_id = prev_saved_map[bank]["account_id"]
        try:
            if budget_id not in api_data.keys():
                raise KeyError
            if account_id not in api_data[budget_id]["accounts"].keys():
                raise KeyError
        except KeyError:
            temp_mapping.setdefault(bank, {"account_id": "", "budget_id": ""})
    return temp_mapping


def select_accounts(
    mappings: dict[str, dict[str, str]], budget_info: dict[str, dict]
):
    for bank in mappings.keys():
        if mappings[bank]["account_id"] == "":
            # get the budget ID and Account ID to write to
            budget_id, account_id = select_account(bank, budget_info)
            mappings[bank]["budget_id"] = budget_id
            mappings[bank]["account_id"] = account_id


def select_account(bank_name: str, budget_info: dict[str, dict]):
    budget_id = ""
    account_id = ""
    instruction = "No YNAB {} for transactions from {} set!\nPick {}"

    # "No YNAB budget for {} set! \nPick a budget".format(bank)
    msg = instruction.format("budget", bank_name, "a budget")

    # generate budget name/id list
    budget_list = generate_name_id_list(budget_info)
    # ask user to select budget
    budget_id = user_input.get_user_input(budget_list, msg)

    # msg = "Pick a YNAB account for transactions from {}".format(bank)
    msg = instruction.format("account", bank_name, "an account")
    # generate account name/id list
    account_dict = budget_info[budget_id]["accounts"]
    account_list = generate_name_id_list(account_dict)
    # ask user to select account
    account_id = user_input.get_user_input(account_list, msg)

    return budget_id, account_id


def generate_name_id_list(input_dict: dict):
    output_list = list()
    for id in input_dict.keys():
        output_list.append([input_dict[id]["name"], id])
    return output_list


def apply_mapping(
    transaction_data: dict[str, list], mapping: dict[str, dict[str, str]]
) -> dict[str, dict[str, list]]:
    """
    Create a dictionary of budget_ids mapped to a dictionary of transactions.
    Add an account_id to each transaction.

    :param transaction_data: dictionary of bank names to transaction data
    :type transaction_data: dict[str, list]
    :param mapping: dictionary mapping bank names to budget ID and account ID
    :type mapping: dict[str, dict[str, str]]
    :return: dictionary of budget_id mapped to a dictionary of transactions
    :rtype: dict[str, dict]
    """
    logging.info("Adding budget and account IDs to transactions...")
    budget_transaction_dict: dict[str, dict[str, list]] = dict()

    # get transactions for each bank
    for bank in transaction_data.keys():
        account_transactions = transaction_data[bank]
        budget_id = mapping[bank]["budget_id"]
        account_id = mapping[bank]["account_id"]

        # insert account_id into each transaction
        for transaction in account_transactions:
            transaction["account_id"] = account_id
        # add transaction list into entry for relevant budget
        if budget_id in budget_transaction_dict:
            budget_transaction_dict[budget_id][
                "transactions"
            ] += account_transactions
        else:
            budget_transaction_dict.setdefault(
                budget_id, {"transactions": account_transactions}
            )

    return budget_transaction_dict
