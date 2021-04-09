import logging
import os
from time import localtime, strftime
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


Job = namedtuple("Job", ("budget", "account", "filename"))


def move_to_history_folder(job):
    root = os.path.join(get_project_dir(), "history")
    prefix = strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())
    folder = os.path.join(root, job.budget.name, job.account.name)
    os.makedirs(folder, exist_ok=True)
    name = prefix + os.path.basename(job.filename)
    os.rename(job.filename, os.path.join(folder, name))


def process_import_tree(bank, budgets, api):
    root = get_import_root()
    jobs = []
    for budget in budgets:
        for account in budget.accounts:
            account_path = os.path.join(root, budget.name, account.name)
            for filename in os.listdir(account_path):
                jobs.append(Job(budget=budget, account=account, filename=os.path.join(account_path, filename)))
    for job in jobs:
        transaction_data = bank.read_data(job.filename)
        if not transaction_data:
            logging.info("No data in file for job: {}".format(job))
            continue
        print(transaction_data)
        api.post_transactions(transaction_data, job.budget.id, job.account.id)
        move_to_history_folder(job)


def main():

    config = get_configs()
    # print(transaction_data)
    api = YNAB_API(config)
    budgets = api.list_budgets()
    print(budgets)
    init_import_root(budgets)

    b2y = Bank2Ynab(config)
    bank_id = "DK Bankernes EDB Central"
    my_bank = b2y.get_bank_by_name(bank_id)
    print(my_bank.name)

    process_import_tree(my_bank, budgets, api)

if __name__ == "__main__":
    main()
