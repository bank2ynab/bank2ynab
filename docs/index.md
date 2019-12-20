# bank2ynab

A common project to consolidate all conversion efforts from various banks' export formats into YNAB's import format.

- [What? (Features)](#what)
  - [Wish List](#wishlist)
- [Why?](#why)
- [How?](#how)
- [Installation Instructions](#install)
  - [Requirements](#requirements)
- [User Guide](#userguide)
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

## <a name="install"></a>Installation Instructions

- Download [this ZIP file](https://github.com/bank2ynab/bank2ynab/archive/master.zip)
- Note the [Requirements](#requirements) for additional details!
- When you're done, refer to the [User Guide](#userguide) below.

### <a name="requirements"></a>Requirements

- Windows or Mac or Linux
- Python v3.5+ installed ([download it from python.org](https://www.python.org/downloads/)) (Python v2.7 *might* work but we make no promises; Py2 has end-of-life on 01Jan2020.)
- Support for other scripting languages may follow. Contributions are welcome!

## <a name="userguide"></a>User Guide

Using `bank2ynab` is easy:

1. Download some bank statements from your banking website.
   - Make sure to choose CSV format. Save with the default suggested filename so that the converter can find it.
   - It's okay if the statements contain data that you already have in YNAB. YNAB will detect and skip these.
1. Check the `[DEFAULT]` configuration in `user_configuration.conf`. *You only need to do this once.* Specifically:
   - `Source Path = c:\users\example-username\Downloads` Specify where you save your downloaded CSV files.
   - `Delete Source File = True` set to `False` if you want to keep the original CSV you downloaded.
1. Check that the configuration in `bank2ynab.conf` contains a `[SECTION]` for your banking format. *You only need to do this once per bank you use.* If you can't find your bank in the config, [tell us your bank's format](https://goo.gl/forms/b7SNwTxmQFfnXlMf2) and we can add it to the project.
1. Run the `bank2ynab.py` conversion script to generate the YNAB-ready CSV output file. How to do this depends on your operating system:
   - Windows: Open a command prompt, navigate to the script directory, and run the command `python bank2ynab.py`.
     - Pro tip: Create a program shortcut! Right-click on the `bank2ynab.bat` file, choose *Send to* and then choose *Desktop (create shortcut)*. Now you can just double-click that shortcut!
   - Linux/Mac: Open a terminal, navigate to the script directory, and run the command `python3 ./bank2ynab.py`.
     - *Important:* Be sure to use `python3` specifically, and not `python` or `python2` which is probably the system default.
 1. Depending on your configuration, the conversion script will now import your files into YNAB automatically, or you can add the files manually:
    - **Automatic import** (when you have provided [your YNAB API access token](https://github.com/bank2ynab/bank2ynab/wiki/Create-your-YNAB-API-access-token): 
      - The conversion script will now ask you which budget it should use to import your converted CSV file to (if you have multiple). It will also ask you which account inside the budget to use (if you have multiple); you'll only have to answer this question once.
    - **Manually drag-and-drop** the converted CSV file onto the YNAB web app:
      - YNAB will detect this and offer you import options. If you had already switched YNAB to the corresponding account view, YNAB will understand that you want to import this file to this account.

## <a name="knownbugs"></a>Known Bugs

For details, please see our [issue list labeled "Bug"](https://github.com/bank2ynab/bank2ynab/issues?q=is%3Aissue+is%3Aopen+label%3Abug).

## <a name="formats"></a>List of Supported Banks

Here is a list of the banks and their formats that we already support. Note that we have many [more formats in the pipeline](https://github.com/bank2ynab/bank2ynab/issues?q=is%3Aopen+is%3Aissue+label%3A%22bank+format%22) so the list continues to grow, and we are happy to receive [requests](https://goo.gl/forms/b7SNwTxmQFfnXlMf2). In alphabetical order (country and bank):

1. AT easybank credit card
1. AT Raiffeisen Bank 2018 checking
1. AT Raiffeisen Bank 2019 checking
1. AT Raiffeisen Bank VISA card
1. BE KBC checking
1. BE BE Keytrade Bank
1. BR Banco do Brasil checking
1. BR Inter checking
1. CA TD Canada Trust, checking+Visa
1. CH Zürcher Kantonalbank, Kontoauszug
1. , Finanzassistent
1. CZ AirBank checking and savings
1. CZ Ceska Sporitelna
1. CZ Raiffeisen bank
1. DE Commerzbank checking
1. DE Consorsbank checking
1. DE Deutsche Bank
1. DE Deutsche Kreditbank checking
1. DE Deutsche Kreditbank credit card
1. DE ING-DiBa
1. DE Kreissparkasse
1. DE N26
1. DE Ostseesparkasse Rostock checking
1. DE Ostseesparkasse Rostock credit card
1. DE Sparkasse Rhein-Neckar-Nord
1. DK Bankernes EDB Central
1. DK Jyske Bank VISA
1. DK Nordea
1. DK Sparkassen Thy
1. HU Erste Bank checking
1. IE AIB Ireland
1. IE Bank of Ireland
1. IE N26
1. IE Ulster Bank, savings
1. MV Bank of Maldives, checking
1. NL Bunq checking
1. NL bunqDesktop software
1. NL ING Bank
1. NL Rabobank (2017 format)
1. NL Rabobank (2018 format)
1. NO DNB
1. NO Sparebank 1 VISA
1. PL mBank, checking
1. SE Handelsbanken
1. SE Länsförsäkringar checking
1. SE Nordea
1. SE SEB, Skandinaviska Enskilda Banken
1. SE Sparbanken Tanum
1. SE Swedbank
1. SE Swedbank (2019 format)
1. SE OCBC Bank
1. SG POSB savings
1. SK Tatra Banka
1. SK VUB
1. UK Barclaycard credit card
1. UK Barclaycard Business Credit Card
1. UK Co-operative Bank
1. UK first direct checking
1. UK Monzo checking
1. US Bank of America
1. US Bank of America Credit Card
1. US BB&T
1. US Chase Credit Card
1. US Schwab
1. US TB Bank
1. (software) Mint
1. (software) Neteller
1. (software) Personal Capital

----

[![XKCD on standards: Fortunately, the charging one has been solved now that we've all standardized on mini-USB. Or is it micro-USB? Shit.](https://imgs.xkcd.com/comics/standards.png)](https://xkcd.com/927/)

----

*Disclaimer: Please use at your own risk. This tool is neither officially supported by YNAB (the company) nor by YNAB (the software) in any way. Use of this tool could introduce problems into your budget that YNAB, through its official support channels, will not be able to troubleshoot or fix. See also the full [MIT licence](https://raw.githubusercontent.com/bank2ynab/bank2ynab/master/LICENSE).*
