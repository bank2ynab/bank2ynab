<!-- I thought about adding some graphics for a better appearance, but it is too large and dominates the page:
![YNAB banner image](https://b.thumbs.redditmedia.com/-4WEzT9WdhQV_khUidt56887E01btV8IILeL6TNvtvI.png)
-->
# bank2ynab
[![Python testing](https://github.com/bank2ynab/bank2ynab/actions/workflows/testing.yml/badge.svg?branch=develop)](https://github.com/bank2ynab/bank2ynab/actions/workflows/testing.yml)
[![GitHub issues by-label](https://img.shields.io/github/issues-raw/bank2ynab/bank2ynab/bug.svg)](https://github.com/bank2ynab/bank2ynab/issues?q=is%3Aissue+is%3Aopen+label%3Abug)
[![GitHub open issues](https://img.shields.io/github/issues-raw/bank2ynab/bank2ynab.svg)](https://github.com/bank2ynab/bank2ynab/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/bank2ynab/bank2ynab.svg)](https://github.com/bank2ynab/bank2ynab/commits/develop)
[![PRs welcome!](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/bank2ynab/bank2ynab/blob/develop/docs/CONTRIBUTING.md)
[![Lint: ruff](https://img.shields.io/badge/lint-ruff-46a2f1.svg)](https://github.com/astral-sh/ruff)
[![Lint](https://github.com/bank2ynab/bank2ynab/actions/workflows/codestyle.yml/badge.svg?branch=develop)](https://github.com/bank2ynab/bank2ynab/actions/workflows/codestyle.yml)

This project consolidates other conversion efforts into one universal tool that easily converts and imports your bank's statements into YNAB.

- [What? (Features)](#what)
  - [Wish List](#wishlist)
- [Why?](#why)
- [How?](#how)
- [Installation Instructions](#install)
  - [Requirements](#requirements)
- [User Guide](#userguide)
- [YNAB API Import](#api)
- [Contributors](#contributors)
- [Known Bugs](#knownbugs)
- [List of Supported Banks](#formats)

## <a name="what"></a>What? (Features)

***Convert your downloaded bank statements into YNAB's input format.*** Here's what this script does, step by step:

1. Look for and parse the `bank2ynab.conf`. This file contains all the rules and import formats.
1. Look for and parse every CSV file in the configured download directory.
1. If the CSV file matches any of the configured formats:
   1. Create a new CSV file in YNAB's CSV format with the correct columns and a blank Category column.
   1. Optionally delete the original CSV file.

### <a name="wishlist"></a>Wish List

- add many more input formats from all the [other YNAB-CSV-conversion projects](https://github.com/search?o=desc&q=ynab+convert&s=updated&type=Repositories&utf8=%E2%9C%93).
- maybe coming later: automatically download your bank statements? (uses external services; only available in some countries)
- maybe coming later: automatically import the converted data into your YNAB app? (optional, default off)

## <a name="why"></a>Why?

There are currently more than 80 GitHub projects related to YNAB converter scripts. Clearly there's a need, but until now these solutions have been fragmented. The present project "bank2ynab" aims to focus the efforts on a common source that encapsulates a large number of bank formats. This will also provide a common basis for a solution using a variety of programming languages.

## <a name="how"></a>How? Contribute!

- If you're "just a user":
  - [tell us your import format](https://goo.gl/forms/b7SNwTxmQFfnXlMf2) and we can create a converter - for you and for everyone else!
  - use the converter provided here and [give us feedback](https://github.com/bank2ynab/bank2ynab/issues/new/choose) - or participate!
- If you've already built a YNAB converter:
  - take advantage of this project to get more import formats.
  - give back to this project by [sharing your existing import formats](https://goo.gl/forms/b7SNwTxmQFfnXlMf2).
- Add a brainstorming item as a [new issue](https://github.com/bank2ynab/bank2ynab/issues/new).
- Join the chat over at https://gitter.im/bank2ynab/Lobby
- See also: [the wiki](https://github.com/bank2ynab/bank2ynab/wiki), perhaps most importantly [this page about import formats](https://github.com/bank2ynab/bank2ynab/wiki/ImportFormats).

## <a name=install></a>Installation Instructions

- Install from PyPI: `pip install bank2ynab`
- Or install from source (recommended for contributors):
  - `git clone https://github.com/bank2ynab/bank2ynab.git`
  - `cd bank2ynab`
  - `uv sync`
- Then follow the [User Guide](#userguide) below.

### <a name="requirements"></a>Requirements

- Windows or Mac or Linux
- Python v3.9+ installed ([download it from python.org](https://www.python.org/downloads/))
- Support for other scripting languages may follow. Contributions are welcome!

Troubleshooting:
- If you see `RequestsDependencyWarning` about `urllib3/chardet/charset_normalizer`, resync the environment with `uv sync --reinstall`.

## <a name="userguide"></a>User Guide

Using `bank2ynab` is easy:

1. Download some bank statements from your banking website.
   - Make sure to choose CSV format. Save with the default suggested filename so that the converter can find it.
   - It's okay if the statements contain data that you already have in YNAB. YNAB will detect and skip these.
1. Run `bank2ynab` once to generate default config files.
   - `user_configuration.conf` is read from `BANK2YNAB_CONFIG_DIR` if that environment variable is set.
   - Otherwise it is read from your OS user config directory for `bank2ynab`.
   - On Windows, that is typically `%LOCALAPPDATA%\bank2ynab\bank2ynab\user_configuration.conf`.
   - Example: `C:\Users\YourName\AppData\Local\bank2ynab\bank2ynab\user_configuration.conf`
1. Check the `[DEFAULT]` configuration in that `user_configuration.conf` file. You only need to do this once.
   - `Source Path = c:\users\example-username\Downloads` sets where downloaded CSV files are read from.
   - `Delete Source File = True` can be set to `False` if you want to keep originals.
1. Check that `bank2ynab.conf` contains a `[SECTION]` for your bank format.
1. Run the converter:
   - If installed from PyPI: `bank2ynab`
   - If running from source: `uv run bank2ynab`
1. If API upload is not configured, import the output CSV manually in YNAB.

## <a name="api"></a>YNAB API Import

Use this section if you want `bank2ynab` to upload transactions directly to YNAB.

1. Create a Personal Access Token in YNAB (`My Account` -> `Developer Settings` -> `Personal Access Tokens`).
1. Open `user_configuration.conf` and set `YNAB API Access Token = <your_token>`.
1. Run `bank2ynab` again.
1. On first API run for each bank section, choose:
   - Budget
   - Account
1. The selected mapping is stored as `YNAB Account ID = <budget_id>||<account_id>` in your user config.

Notes:
- Config location:
  - `BANK2YNAB_CONFIG_DIR` if set.
  - Otherwise your OS default user config directory for `bank2ynab`.
- Windows example:
  - `%LOCALAPPDATA%\bank2ynab\bank2ynab\user_configuration.conf`
- Root-level config files in the project directory are no longer used.
- If `Save YNAB Account = True`, account mapping is reused automatically.
- If token is blank, API upload is skipped and output remains CSV-based.
- Keep your token private.

## <a name="contributors"></a>Contributors

[![Contributors](https://contrib.rocks/image?repo=bank2ynab/bank2ynab)](https://github.com/bank2ynab/bank2ynab/graphs/contributors)

## <a name="knownbugs"></a>Known Bugs

For details, please see our [issue list labeled "Bug"](https://github.com/bank2ynab/bank2ynab/issues?q=is%3Aissue+is%3Aopen+label%3Abug).

## <a name="formats"></a>List of Supported Banks

Here is a list of the banks and their formats that we already support. Note that we have many [more formats in the pipeline](https://github.com/bank2ynab/bank2ynab/issues?q=is%3Aopen+is%3Aissue+label%3A%22bank+format%22) so the list continues to grow, and we are happy to receive [requests](https://goo.gl/forms/b7SNwTxmQFfnXlMf2). In alphabetical order (country and bank):
<!--AUTO BANK UPDATE START-->
1. AT easybank credit card
1. AT Raiffeisen Bank 2018
1. AT Raiffeisen Bank RCM
1. AT Raiffeisen Bank 2019 checking
1. AT Raiffeisen Bank 2021 checking
1. AT Raiffeisen VISA
1. AU ANZ
1. AU ING
1. AU National Australia Bank
1. BE BNP Paribas Fortis old
1. BE BNP Paribas Fortis Export
1. BE KBC checking
1. BE KBC credit
1. BE Keytrade Bank
1. BR Banco Bradesco Checking
1. BR Banco do Brasil, checking
1. BR Inter, checking
1. CA TD Canada Trust, checking+Visa
1. CH UBS Checking account
1. CH UBS Checking account - Alternative 1
1. CH UBS Credit card
1. CH Neon Monthly Account Statement
1. CH Neon Yearly Account Statement
1. CH SwissCard
1. CH ZKB Konto CSV-Export (Mit Details)
1. CH ZKB Erweiterte Suche
1. CH ZKB Finanzassistent-Chronik
1. CH ZugerKB Kontoauszug
1. CO Bancolombia
1. Crypto.com
1. CZ AirBank checking and savings
1. CZ Ceska Sporitelna
1. CZ Raiffeisen bank
1. DE Amazon VISA LBB
1. DE Commerzbank checking
1. DE Consorsbank checking
1. DE Deutsche Bank
1. DE Deutsche Bank Credit Card
1. DE Deutsche Kreditbank checking
1. DE Deutsche Kreditbank checking new
1. DE Deutsche Kreditbank credit card
1. DE Fiducia (Volksbank, Sparda-Bank, BBBank, PSD Bank, Raiffeisen, ...)
1. DE ING-DiBa
1. DE Kreissparkasse
1. DE N26
1. DE Ostseesparkasse Rostock checking
1. DE Ostseesparkasse Rostock credit card
1. DE Sparkasse Rhein-Neckar-Nord
1. DE Sparkasse Südholstein
1. DK Bankernes EDB Central
1. DK Danske Bank
1. DK Jyske Bank VISA
1. DK Nordea
1. DK Portalbank
1. Hibiscus banking software
1. HU Erste Bank checking
1. HU K&H
1. HU OTP
1. IE AIB Ireland
1. IE Bank of Ireland
1. IE First South Credit Union
1. IE N26
1. IE Ulster Bank, savings
1. IT RomagnaBanca Inbank
1. LV Swedbank
1. Mint
1. MV Bank of Maldives, checking
1. NETELLER
1. NL American Express (AMEX)
1. NL Bunq checking
1. NL bunqDesktop software
1. NL bunqDesktop software 2
1. NL ING
1. NL ING Checking 2020
1. NL KNAB
1. NL Rabobank
1. NL Rabobank-2018
1. NL RegioBank
1. NL Rabobank Credit Card
1. NO DNB
1. NO Sparebank 1 VISA
1. Personal Capital
1. PL Alior Bank
1. PL mBank
1. PL PKO BP
1. PL Bank Pekao
1. Revolut
1. SE Handelsbanken
1. SE Länsförsäkringar checking
1. SE Morrow Bank
1. SE Nordea - internetbanken.privat.nordea.se
1. SE Nordea - netbank.nordea.se
1. SE SEB Skandinaviska Enskilda Banken
1. SE Sparbanken Tanum
1. SE Swedbank
1. SE Swedbank 2019
1. SE Swedbank 2020
1. SG HSBC Savings Account
1. SG HSBC Credit Card
1. SG OCBC Bank
1. SG OCBC Bank Credit Card
1. SG POSB savings
1. SG UOB Savings Account
1. SG UOB Credit Card
1. SK Tatra Banka
1. SK VUB
1. UK Co-operative Bank
1. UK Monzo checking
1. UK Barclaycard credit card
1. UK Barclaycard Business Credit Card
1. UK first direct checking
1. UK John Lewis Partnership Card (Pre-2022 Format)
1. UK John Lewis Partnership Card (NewDay Format)
1. US Bank of America
1. US Bank of America Credit Card
1. US BB&T
1. US Chase Credit Card 2017
1. US Chase Credit Card 2019
1. US Fidelity CMA
1. US Schwab Checking
1. US Schwab Savings
1. US TB Bank
1. US USAA
1. Wise
<!--AUTO BANK UPDATE END-->
----

[![XKCD on standards: Fortunately, the charging one has been solved now that we've all standardized on mini-USB. Or is it micro-USB? Shit.](https://imgs.xkcd.com/comics/standards.png)](https://xkcd.com/927/)

----

*Disclaimer: Please use at your own risk. This tool is neither officially supported by YNAB (the company) nor by YNAB (the software) in any way. Use of this tool could introduce problems into your budget that YNAB, through its official support channels, will not be able to troubleshoot or fix. See also the full [MIT licence](https://raw.githubusercontent.com/bank2ynab/bank2ynab/master/LICENSE).*
