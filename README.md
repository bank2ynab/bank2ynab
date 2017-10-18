# bank2ynab
A common project to consolidate all conversion efforts from various banks' export formats into YNAB's import format.

## Why?

There are currently more than 80 GitHub projects related to YNAB converter scripts. Clearly there's a need, but until now these solutions have been fragmented. The present project "bank2ynab" aims to focus the efforts on a common source that encapsulates a large number of bank formats. This will also provide a common basis for a solution using a variety of programming languages.

## How? Contribute!

- If you're "just a user":
  - tell us your import format and we can create a converter - for you and for everyone else!
  - use the converter provided here and give us feedback - or participate!
- If you've already built a YNAB converter:
  - take advantage of this project to get more import formats.
  - give back to this project by sharing your existing import formats.
- add a brainstorming item as a new issue in the [issue list](https://github.com/torbengb/bank2ynab/issues)
- read or add to the [wiki](https://github.com/torbengb/bank2ynab/wiki) and most importantly the [list of bank formats](https://github.com/torbengb/bank2ynab/wiki/ImportFormats).

## Features

***Convert your downloaded bank statements into YNAB's input format.*** Here's what this script does, step by step:

1. Look for and parse the `config.conf`. This file contains all the rules and import formats.
1. Look for and parse every CSV file in the configured download directory.
1. If the CSV file matches any of the configured formats: 
   1. create a new CSV file using YNAB's CSV format. 
   1. Fill the new file with the correct columns.
   1. Add a blank Category column.
   1. Optionally swap columns `Payee` and `Memo`.
   1. Optionally delete the original CSV file.

## Requirements

- Windows or Mac or Linux
- Support for Python, or Ruby, or some other scripting language (to be defined)

## Wish List

- add many more input formats from all the other YNAB-CSV-conversion projects.
- maybe coming later: automatically download your bank statements? (uses external services; only available in some countries)

----

![XKCD on standards](https://imgs.xkcd.com/comics/standards.png)


