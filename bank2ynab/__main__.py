import logging
import os
from collections import namedtuple

from b2y_utilities import get_configs, get_project_dir
from bank_process import Bank2Ynab
from ynab_api import YNAB_API

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

def get_import_root():
    return os.path.join(get_project_dir(), "imports")


def init_import_root(budgets):
    """
    Create a directory structure matching the account names on ynab
    :return:
    """
    root = get_import_root()
    for b in budgets:
        for a in b.accounts:
            os.makedirs(os.path.join(root, b.name, a.name), exist_ok=True)


Job = namedtuple("Job", ("budget", "account", "file"))


def move_to_history_folder(j):
    root = os.path.join(get_project_dir(), "history")
    prefix = ""  # TODO "timestamp-now"
    folder = os.path.join(root, j.budget.name, j.account.name)
    os.makedirs(folder, exist_ok=True)
    name = prefix + os.path.basename(j.file)
    os.rename(j.file, os.path.join(folder, name))


def process_import_tree(bank, budgets, api):
    root = get_import_root()
    jobs = []
    for b in budgets:
        for a in b.accounts:
            account_path = os.path.join(root, b.name, a.name)
            for f in os.listdir(account_path):
                jobs.append(Job(budget=b, account=a, file=os.path.join(account_path, f)))
    for j in jobs:
        transaction_data = bank.read_data(j.file)
        if not transaction_data:
            logging.info("No data in file for job: {}".format(j))
            continue
        print(transaction_data)
        api.post_transactions(transaction_data, j.budget.id, j.account.id)
        move_to_history_folder(j)


if __name__ == "__main__":
    bank_id = "DK Bankernes EDB Central"
    file = "/home/jacob/Downloads/Al_jacob.csv"
    config = get_configs()

    b2y = Bank2Ynab(config)
    my_bank = b2y.get_bank_by_name(bank_id)
    print(my_bank.name)
    # transaction_data = my_bank.process_file(file)
    # print(transaction_data)
    api = YNAB_API(config)
    budgets = api.list_budgets()
    print(budgets)
    init_import_root(budgets)
    process_import_tree(my_bank, budgets, api)
