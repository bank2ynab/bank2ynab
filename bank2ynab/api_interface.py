import logging

import requests

from ynab_api_response import YNABError


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
                budget_accounts = get_budget_accounts(
                    api_token=api_token, budget_id=budget_id
                )
                budget_dict[budget_id]["accounts"] = budget_accounts
            self.budget_info = budget_dict
            logging.info("All budget and account data obtained.")
        else:
            logging.info("No API-token provided.")


def access_api(
    api_token: str, budget_id: str, keyword: str, method: str, data: str
) -> dict:
    base_url = "https://api.youneedabudget.com/v1/budgets/"

    if budget_id == "":
        # only happens when we're looking for the list of budgets
        url = base_url + f"?access_token={api_token}"
    else:
        url = base_url + f"{budget_id}/{keyword}?access_token={api_token}"

    if method == "post":
        logging.info(f"\tSending '{keyword}' data to YNAB API...")
        with (open("test_data.json", "w")) as f:
            f.write(data)
        data1 = {
            "transactions": [
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-02",
                    "payee_name": "Niall O Callaghan",
                    "amount": 2566570,
                    "memo": "Niall O Callaghan",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:2566570:2021-12-02:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-03",
                    "payee_name": "Super Valu Togher The Lough T12N67A Eur",
                    "amount": -5590,
                    "memo": "Super Valu Togher The Lough T12N67A Eur",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-5590:2021-12-03:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-06",
                    "payee_name": "Super Valu Togher The Lough T12N67A Eur",
                    "amount": -15050,
                    "memo": "Super Valu Togher The Lough T12N67A Eur",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-15050:2021-12-06:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-08",
                    "payee_name": "Dunnes Douglas Court Douglas Cork Eur",
                    "amount": -15670,
                    "memo": "Dunnes Douglas Court Douglas Cork Eur",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-15670:2021-12-08:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-09",
                    "payee_name": "Niamhoregan",
                    "amount": 6150000,
                    "memo": "Niamhoregan",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:6150000:2021-12-09:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-09",
                    "payee_name": (
                        "0928 Lidl Togher Southside Shoppi Lidl Ireland Eur"
                    ),
                    "amount": -18980,
                    "memo": (
                        "0928 Lidl Togher Southside Shoppi Lidl Ireland Eur"
                    ),
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-18980:2021-12-09:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-11",
                    "payee_name": (
                        "0928 Lidl Togher Southside Shoppi Lidl Ireland Eur"
                    ),
                    "amount": -12290,
                    "memo": (
                        "0928 Lidl Togher Southside Shoppi Lidl Ireland Eur"
                    ),
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-12290:2021-12-11:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-13",
                    "payee_name": "Spotify Regeringsg Stockholm Eur",
                    "amount": -13990,
                    "memo": "Spotify Regeringsg Stockholm Eur",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-13990:2021-12-13:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-14",
                    "payee_name": "Vistaprint Hudsonweg 8 Venlo Eur",
                    "amount": -87030,
                    "memo": "Vistaprint Hudsonweg 8 Venlo Eur",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-87030:2021-12-14:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-14",
                    "payee_name": (
                        "0928 Lidl Togher Southside Shoppi Lidl Ireland Eur"
                    ),
                    "amount": -38200,
                    "memo": (
                        "0928 Lidl Togher Southside Shoppi Lidl Ireland Eur"
                    ),
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-38200:2021-12-14:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-14",
                    "payee_name": "P O Connell Son Foo The Lough Cork Eur",
                    "amount": -27850,
                    "memo": "P O Connell Son Foo The Lough Cork Eur",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-27850:2021-12-14:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-16",
                    "payee_name": "Eir Ltd",
                    "amount": -65990,
                    "memo": "Eir Ltd",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-65990:2021-12-16:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-17",
                    "payee_name": "Super Valu Togher The Lough T12N67A Eur",
                    "amount": -21980,
                    "memo": "Super Valu Togher The Lough T12N67A Eur",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-21980:2021-12-17:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-18",
                    "payee_name": (
                        "Netflix Com Keizersgracht 440 2Nd 866 579 7172 Eur"
                    ),
                    "amount": -12990,
                    "memo": (
                        "Netflix Com Keizersgracht 440 2Nd 866 579 7172 Eur"
                    ),
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-12990:2021-12-18:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-19",
                    "payee_name": (
                        "The Roughty Foodie Unit 20 English Market Cork Eur"
                    ),
                    "amount": -17500,
                    "memo": (
                        "The Roughty Foodie Unit 20 English Market Cork Eur"
                    ),
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-17500:2021-12-19:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-19",
                    "payee_name": (
                        "Mr Bells Global Food Unit 25 The English Cork Eur"
                    ),
                    "amount": -16200,
                    "memo": (
                        "Mr Bells Global Food Unit 25 The English Cork Eur"
                    ),
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-16200:2021-12-19:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-20",
                    "payee_name": (
                        "Market Lane Rest Bar 5 6 Oliver T12T959 Eur"
                    ),
                    "amount": -13100,
                    "memo": "Market Lane Rest Bar 5 6 Oliver T12T959 Eur",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-13100:2021-12-20:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-21",
                    "payee_name": "Caledonian Life",
                    "amount": -18470,
                    "memo": "Caledonian Life",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-18470:2021-12-21:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-23",
                    "payee_name": (
                        "0928 Lidl Togher Southside Shoppi Lidl Ireland Eur"
                    ),
                    "amount": -40100,
                    "memo": (
                        "0928 Lidl Togher Southside Shoppi Lidl Ireland Eur"
                    ),
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-40100:2021-12-23:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-24",
                    "payee_name": (
                        "0928 Lidl Togher Southside Shoppi Lidl Ireland Eur"
                    ),
                    "amount": -15010,
                    "memo": (
                        "0928 Lidl Togher Southside Shoppi Lidl Ireland Eur"
                    ),
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-15010:2021-12-24:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-25",
                    "payee_name": "Petstop Kinsale Ro Cork Eur",
                    "amount": -37640,
                    "memo": "Petstop Kinsale Ro Cork Eur",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-37640:2021-12-25:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-25",
                    "payee_name": (
                        "Applegreen Youghal Upp Applegreen Youghal Eur"
                    ),
                    "amount": -49910,
                    "memo": "Applegreen Youghal Upp Applegreen Youghal Eur",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-49910:2021-12-25:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2021-12-29",
                    "payee_name": "Iberdrola Irlanda",
                    "amount": -173310,
                    "memo": "Iberdrola Irlanda",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-173310:2021-12-29:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2019-12-12",
                    "payee_name": "Royal London Insurance 01222 61234 Gbr",
                    "amount": -1183230,
                    "memo": "Royal London Insurance 01222 61234 Gbr",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-1183230:2019-12-12:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2019-12-12",
                    "payee_name": "Deliveroo Co Uk London Lnd",
                    "amount": -18890,
                    "memo": "Deliveroo Co Uk London Lnd",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-18890:2019-12-12:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2019-12-12",
                    "payee_name": "Nooki Design London Nw10 Gbr",
                    "amount": -23000,
                    "memo": "Nooki Design London Nw10 Gbr",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-23000:2019-12-12:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2019-12-12",
                    "payee_name": "Next Directory Online Gbr",
                    "amount": -80990,
                    "memo": "Next Directory Online Gbr",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-80990:2019-12-12:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2019-12-03",
                    "payee_name": "Tfl Travel Ch Tfl Gov Uk Cp Gbr",
                    "amount": -1500,
                    "memo": "Tfl Travel Ch Tfl Gov Uk Cp Gbr",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-1500:2019-12-03:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2019-12-03",
                    "payee_name": "Space Nk Ltd Kensington Gbr",
                    "amount": -50000,
                    "memo": "Space Nk Ltd Kensington Gbr",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-50000:2019-12-03:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2019-12-03",
                    "payee_name": "V A Museum Sales London Gbr",
                    "amount": -10000,
                    "memo": "V A Museum Sales London Gbr",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-10000:2019-12-03:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2019-12-02",
                    "payee_name": "Spotify Uk London Gbr",
                    "amount": -9990,
                    "memo": "Spotify Uk London Gbr",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-9990:2019-12-02:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2019-12-02",
                    "payee_name": "Sainsburys Sacat 0602 Ladbroke Grov Gbr",
                    "amount": -8200,
                    "memo": "Sainsburys Sacat 0602 Ladbroke Grov Gbr",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-8200:2019-12-02:1",
                },
                {
                    "account_id": "89feb376-a5a9-4761-bae1-bb2fb140773e",
                    "date": "2019-12-02",
                    "payee_name": "Payment Received Thank You",
                    "amount": -1100000,
                    "memo": "Payment Received Thank You",
                    "category": "",
                    "cleared": "cleared",
                    "import_id": "YNAB:-1100000:2019-12-02:1",
                },
            ]
        }
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
            data="",
        )
    except YNABError as e:
        logging.error(f"YNAB API Error: {e}")
    return return_data[keyword]


def post_transactions(api_token: str, budget_id: str, data: str) -> None:
    """
    Send transaction data to YNAB via API call

    :param api_token: API token to access YNAB API
    :type api_token: str
    :param budget_id: id of budget to post transactions to
    :type budget_id: str
    :param data: transaction data in json format
    :type data: str
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
    """
    Combines response data JSON into a dictionary mapping ID to response data.

    :param input_data: JSON-style dictionary
    :type input_data: dict
    :return: dictionary mapping "id" to response data
    :rtype: dict[str, dict]
    """
    output_dict = dict()
    for sub_dict in input_data:
        output_dict.setdefault(sub_dict["id"], sub_dict)
    return output_dict


def get_budget_accounts(api_token: str, budget_id: str) -> dict[str, dict]:
    """
    Returns dictionary matching account id to list of account parameters.

    :param api_token: API token to access YNAB API
    :type api_token: str
    :param budget_id: budget ID to read account data from
    :type budget_id: str
    :return: dictionary mapping account id to parameters
    :rtype: dict[str, dict]
    """
    accounts = api_read(
        api_token=api_token, budget_id=budget_id, keyword="accounts"
    )
    return fix_id_based_dicts(accounts)


def get_budgets(
    api_token: str,
) -> dict[str, dict]:
    """
    Returns dictionary matching budget id to list of budget parameters.

    :param api_token: API token to access YNAB API
    :type api_token: str
    :return: dictionary mapping budget id to parameters
    :rtype: dict[str, dict[str, str]]
    """
    budgets = api_read(api_token=api_token, budget_id="", keyword="budgets")
    return fix_id_based_dicts(budgets)
