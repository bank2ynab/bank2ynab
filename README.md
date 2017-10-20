<!-- I thought about adding some graphics for a better appearance, but it is too large and dominates the page:
![YNAB banner image](https://b.thumbs.redditmedia.com/-4WEzT9WdhQV_khUidt56887E01btV8IILeL6TNvtvI.png)
-->
# bank2ynab
A common project to consolidate all conversion efforts from various banks' export formats into YNAB's import format.

- [What? (Features)](#what)
- [Why?](#why)
- [How?](#how)
- [Wish List](#wishlist)
- [Requirements](#requirements)
- [User Guide](#userguide)
- [Known Bugs](#knownbugs)

## <a name="what"></a>What? (Features)

***Convert your downloaded bank statements into YNAB's input format.*** Here's what this script does, step by step:

1. Look for and parse the `config.conf`. This file contains all the rules and import formats.
1. Look for and parse every CSV file in the configured download directory.
1. If the CSV file matches any of the configured formats: 
   1. create a new CSV file using YNAB's CSV format. 
   1. Fill the new file with the correct columns.
   1. Add a blank Category column.
   1. Optionally swap columns `Payee` and `Memo`.
   1. Optionally delete the original CSV file.

## <a name="why"></a>Why?

There are currently more than 80 GitHub projects related to YNAB converter scripts. Clearly there's a need, but until now these solutions have been fragmented. The present project "bank2ynab" aims to focus the efforts on a common source that encapsulates a large number of bank formats. This will also provide a common basis for a solution using a variety of programming languages.

## <a name="how"></a>How? Contribute!

- If you're "just a user":
  - [tell us your import format](https://goo.gl/forms/b7SNwTxmQFfnXlMf2) and we can create a converter - for you and for everyone else!
  - use the converter provided here and [give us feedback](https://github.com/torbengb/bank2ynab/issues/new) - or participate!
- If you've already built a YNAB converter:
  - take advantage of this project to get more import formats.
  - give back to this project by [sharing your existing import formats](https://goo.gl/forms/b7SNwTxmQFfnXlMf2).
- Add a brainstorming item as a [new issue](https://github.com/torbengb/bank2ynab/issues/new).

## <a name="wishlist"></a>Wish List

- add many more input formats from all the other YNAB-CSV-conversion projects.
- maybe coming later: automatically download your bank statements? (uses external services; only available in some countries)

## <a name="requirements"></a>Requirements

- Windows or Mac or Linux
- Python version 3 installed ([download it from python.org](https://www.python.org/downloads/))
  - we are looking into supporting Python version 2 as well. Work in progress.
  - *(to do @torbengb : dependencies?)*
- Support for other scripting languages may follow. Contributions are welcome!

## <a name="userguide"></a>User Guide

Using `bank2ynab` is easy:

1. Download some bank statements from your banking website.
   - Make sure to choose CSV format. Save with the default suggested filename so that the converter can find it. 
   - It's okay if the statements contain data that you already have in YNAB. YNAB will detect and skip these.
1. Check the `[DEFAULT]` configuration in `bank2ynab.conf`. *You only need to do this once.* Specifically:
   - `Source Path = c:\users\example-username\Downloads` Specify where you save your downloaded CSV files. 
   - `Delete Source File = True` set to `False` if you want to keep the original CSV you downloaded.
1. Check that the configuration in `bank2ynab.conf` contains a `[SECTION]` for your banking format. *You only need to do this once per bank you use.* If you can't find your bank in the config, [tell us your bank's format](https://goo.gl/forms/b7SNwTxmQFfnXlMf2) and we can add it to the project.
1. Run the `bank2ynab.py` conversion script to receive the YNAB-ready CSV output file. How to do this depends on your operating system:
   - Windows: Open a command prompt, navigate to the script directory, and run the command `python bank2ynab.py`.
     - Pro tip: Create a program shortcut! Right-click on the `bank2ynab.py` file, choose *Send to* and then choose *Desktop (as shortcut)*. Now you can just double-click that shortcut.
   - Linux/Mac: Open a terminal, navigate to the script directory, and run the command `python ./bank2ynab.py`.
1. Drag-and-drop the converted CSV file onto the YNAB web app. 
   - YNAB will detect this and offer you import options. If you had already switched YNAB to the corresponding account view, YNAB will understand that you want to import this file to this account.

## <a name="knownbugs"></a>Known Bugs

For details, please see our [issue list labeled "Bug"](https://github.com/torbengb/bank2ynab/issues?q=is%3Aissue+is%3Aopen+label%3Abug).

----

![XKCD on standards](https://imgs.xkcd.com/comics/standards.png)

----

*Disclaimer: This tool is neither officially supported by YNAB (the company) nor by YNAB (the software) in any way. Use of this tool could introduce problems into your budget that YNAB, through its official support channels, will not be able to troubleshoot or fix. Please use at your own risk!*
