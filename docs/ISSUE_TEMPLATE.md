* Dear submitter, please edit the following according to your needs. Thank you!
* Delete "Issue Report" or "Bank Format Addition" as appropriate.

# Issue Report:
Script language: Python 3.5, Python 2.7, other?
Operating system: Windows, Linux, MacOS?
OS Version: 

What did you DO? (steps to reproduce)
...

What did you EXPECT to happen?
...

What ACTUALLY happened?
...

Can you provide other helpful information?
...


# Bank Format Addition
Name of Bank:
Country:
Special Requirements:
...

**To be filled in as required. Delete fields that match default values:**
```
Source Filename Pattern = example_transaction_export_filename
Source Filename Extension = .csv
Use Regex for Filename = False
Source CSV Delimiter = ,
Header Rows = 1
Footer Rows = 0
Input Columns = Date,Payee,Outflow,Inflow,Running Balance
# (see https://docs.python.org/2/library/datetime.html#id1 for date format strings)
Date Format = 
Inflow or Outflow Indicator =
Output Columns = Date,Payee,Category,Memo,Outflow,Inflow
Output Filename Prefix = fixed_
Delete Source File = True
Plugin =
```
