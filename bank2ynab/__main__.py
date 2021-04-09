import logging
import os
import json
from time import localtime, strftime
from collections import namedtuple


from b2y_utilities import get_configs, get_project_dir
from bank_process import Bank2Ynab
from ynab_api import YNAB_API

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

CONFIG_FILE="account_info.json"

def get_import_root():
    return os.path.join(get_project_dir(), "imports")


def init_import_root(budgets):
    """
    Create a directory structure matching the account names on ynab
    :return:
    """
    root = get_import_root()
    for budget in budgets:
        for account in budget.accounts:
            folder = os.path.join(root, budget.name, account.name)
            os.makedirs(folder, exist_ok=True)
            config = os.path.join(folder, CONFIG_FILE)
            if not os.path.exists(config):
                with open(config, "w") as f:
                    json.dump({"bank_id": "DK Bankernes EDB Central"}, f)


Job = namedtuple("Job", ("budget", "account", "filename", "bank_id"))


def move_to_history_folder(job):
    root = os.path.join(get_project_dir(), "history")
    prefix = strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())
    folder = os.path.join(root, job.budget.name, job.account.name)
    os.makedirs(folder, exist_ok=True)
    name = prefix + os.path.basename(job.filename)
    os.rename(job.filename, os.path.join(folder, name))


def process_import_tree(b2y, budgets, api):
    root = get_import_root()
    jobs = []
    for budget in budgets:
        for account in budget.accounts:
            account_path = os.path.join(root, budget.name, account.name)
            bank_id = "DK Bankernes EDB Central"
            config = os.path.join(account_path, CONFIG_FILE)
            with open(config, "r") as f:
                bank_id = json.load(f)["bank_id"]

            for filename in os.listdir(account_path):
                jobs.append(Job(budget=budget, account=account, filename=os.path.join(account_path, filename), bank_id = bank_id))
    for job in jobs:
        bank = b2y.get_bank_by_name(job.bank_id)
        logging.info("Process job {}".format(job))
        transaction_data = bank.read_data(job.filename)
        if not transaction_data:
            logging.info("No data in file for job: {}".format(job))
            continue
        print(transaction_data)
        api.post_transactions(transaction_data, job.budget.id, job.account.id)
        move_to_history_folder(job)


def main():
    config = get_configs()
    api = YNAB_API(config)
    budgets = api.list_budgets()
    print(budgets)
    init_import_root(budgets)

    b2y = Bank2Ynab(config)
    process_import_tree(b2y, budgets, api)

if __name__ == "__main__":
    main()
