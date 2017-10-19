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

***Convert your downloaded bank statements into YNAB's input format.*** 

`bank2ynab` can be easily extended to handle more banks' CSV formats. It uses Python and if there is interest, the project could also include the same solution using other programming languages. Here's what this script does, step by step:

1. Look for and parse the `bank2ynab.conf`. This file contains all the rules and import formats.
1. Look for and parse every CSV file in the configured download directory.
1. If the CSV file matches any of the configured formats: 
   1. create a new CSV file using YNAB's CSV format, and fill the new file with the correct column order. Also add a blank `Category` column.
   1. Optionally swap columns `Payee` and `Memo`.
   1. Optionally delete the original CSV file.

## <a name="why"></a>Why?

There are currently more than 80 GitHub projects related to YNAB converter scripts. Clearly there's a need, but until now these solutions have been fragmented. The present project "bank2ynab" aims to focus the efforts on a common source that encapsulates a large number of bank formats. This will also provide a common basis for a solution using a variety of programming languages.

## <a name="how"></a>How? Contribute!

- If you're "just a user":
  - tell us your import format and we can create a converter - for you and for everyone else!
  - use the converter provided here and give us feedback - or participate!
- If you've already built a YNAB converter:
  - take advantage of this project to get more import formats.
  - give back to this project by sharing your existing import formats.
- add a brainstorming item as a new issue in the [issue list](https://github.com/torbengb/bank2ynab/issues)
- read or add to the [wiki](https://github.com/torbengb/bank2ynab/wiki) and most importantly the [list of bank formats](https://github.com/torbengb/bank2ynab/wiki/ImportFormats).

## <a name="wishlist"></a>Wish List

- primary goal: add many more input formats from all the other YNAB-CSV-conversion projects.
- maybe coming later: automatically download your bank statements? (uses [external services](https://teller.io/); only available in some countries)
- maybe coming later: automatically import the converted file into your YNAB?

## <a name="requirements"></a>Requirements

- Windows or Mac or Linux
- Support for Python, or Ruby, or some other scripting language (to be defined)
  - currently Python v3.x is supported

## <a name="userguide"></a>User Guide

Using `bank2ynab` is easy:

- Download some bank statements from your banking website.
  - Make sure to choose CSV format.
  - *(to do @torbengb : save with default filename?)*
  - It's okay if the statements contain data that you already have in YNAB. YNAB will detect and skip these.
- Check the `[DEFAULT]` configuration in `bank2ynab.conf`. *You only need to do this once.* Specifically:
  - `Source Path =` the path where you save your downloaded CSV files.
  - `Delete Source File = True` set to `False` if you want to keep the original CSV you downloaded.
- Check that the configuration in `bank2ynab.conf` contains a `[SECTION]` for your banking format. *You only need to do this once per bank you use.* We can do this for you (and improve our project) if you [submit a ticket here](https://github.com/torbengb/bank2ynab/issues/new).
  - *(to do @torbengb : more details to be added here!)*
  - `Source Filename Pattern =` *to do*
  - `Source CSV Delimiter = ,` some banks use `;` as a delimiter instead.
  - `Source Has Column Headers = True` set to `False` if it's not the case.
  - `Input Columns = Date,Payee,Outflow,Inflow,Running Balance` modify the order to match your file. Enter `skip` for irrelevant columns.
- Run the `bank2ynab` conversion script. How to do this depends on your operating system:
  - *(to do: more details to be added here!)*
- Drag-and-drop the converted CSV file onto the YNAB web app. 
  - Protip: Switch to the corresponding account view in YNAB first. YNAB will understand that you want to import this CSV file to this YNAB account.

## <a name="knownbugs"></a>Known Bugs

For details, please see our [issue list labeled "Bug"](https://github.com/torbengb/bank2ynab/issues?q=is%3Aissue+is%3Aopen+label%3Abug).

----

![XKCD on standards](https://imgs.xkcd.com/comics/standards.png)

----

*Disclaimer: This tool is neither officially supported by YNAB (the company) nor by YNAB (the software) in any way. Use of this tool could introduce problems into your budget that YNAB, through its official support channels, will not be able to troubleshoot or fix. Please use at your own risk!*
