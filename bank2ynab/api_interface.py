import logging

import requests

from .ynab_api_response import YNABError


class APIInterface:
    def __init__(self, api_token: str) -> None:
        # dict mapping {budget_id: {budget_params}}
        self.budget_info: dict[str, dict] = dict()
        logging.info("Attempting to connect to YNAB API...")
        if api_token is not None:
            logging.info("Obtaining budget and account data...")
            # create budget parameter dictionary
            budget_dict = get_budgets(api_token=api_token)
            # add accounts dictionary to each budget in dict
            for budget_id in budget_dict.keys():
                budget_accounts = get_budget_accounts(api_token=api_token, budget_id=budget_id)
                budget_dict[budget_id]["accounts"] = budget_accounts
            self.budget_info = budget_dict
            logging.info("All budget and account data obtained.")
        else:
            logging.info("No API-token provided.")


def access_api(api_token: str, budget_id: str, keyword: str, method: str, data: dict) -> dict:
    base_url = "https://api.youneedabudget.com/v1/budgets/"

    if budget_id == "":
        # only happens when we're looking for the list of budgets
        url = base_url + f"?access_token={api_token}"
    else:
        url = base_url + f"{budget_id}/{keyword}?access_token={api_token}"

    if method == "post":
        logging.info(f"\tSending '{keyword}' data to YNAB API...")

        response = requests.post(url, json=data)
    else:
        logging.info(f"\tReading '{keyword}' data from YNAB API...")
        response = requests.get(url)

    response_data = dict()
    try:
        response_data = response.json()["data"]
    except KeyError:
        # the API has returned an error so let's handle it
        error_json = response.json()["error"]
        raise YNABError(error_json["id"], error_json["detail"]) from None
    return response_data


def api_read(api_token: str, budget_id: str, keyword: str) -> dict:
    return_data = dict()
    try:
        return_data = access_api(
            api_token=api_token,
            budget_id=budget_id,
            keyword=keyword,
            method="get",
            data={},
        )
    except YNABError as e:
        logging.error(f"YNAB API Error: {e}")
    return return_data[keyword]


def post_transactions(api_token: str, budget_id: str, data: dict) -> None:
    """Send transaction data to YNAB via API call.

    Args:
        api_token: API token to access YNAB API.
        budget_id: ID of budget to post transactions to.
        data: Transaction data in JSON format.
    """

    logging.info("Uploading transactions to YNAB...")
    try:
        response = access_api(
            api_token=api_token,
            budget_id=budget_id,
            keyword="transactions",
            method="post",
            data=data,
        )
        logging.info(
            f"Success: {len(response['transaction_ids'])}"
            " entries uploaded,"
            f" {len(response['duplicate_import_ids'])}"
            " entries skipped."
        )
    except YNABError as e:
        logging.error(f"YNAB API Error: {e}")


def fix_id_based_dicts(input_data: dict) -> dict[str, dict]:
    """Combine response data JSON into a dictionary mapping ID to response data.

    Args:
        input_data: JSON-style dictionary.

    Returns:
        dict[str, dict]: Dictionary mapping "id" to response data.
    """
    output_dict = dict()
    for sub_dict in input_data:
        output_dict.setdefault(sub_dict["id"], sub_dict)
    return output_dict


def get_budget_accounts(api_token: str, budget_id: str) -> dict[str, dict]:
    """Return dictionary matching account id to list of account parameters.

    Args:
        api_token: API token to access YNAB API.
        budget_id: Budget ID to read account data from.

    Returns:
        dict[str, dict]: Dictionary matching account id to parameters.
    """
    accounts = api_read(api_token=api_token, budget_id=budget_id, keyword="accounts")
    return fix_id_based_dicts(accounts)


def get_budgets(
    api_token: str,
) -> dict[str, dict]:
    """Return dictionary matching budget id to list of budget parameters.

    Args:
        api_token: API token to access YNAB API.

    Returns:
        dict[str, dict[str, str]]: Dictionary matching budget id to parameters.
    """
    budgets = api_read(api_token=api_token, budget_id="", keyword="budgets")
    return fix_id_based_dicts(budgets)
