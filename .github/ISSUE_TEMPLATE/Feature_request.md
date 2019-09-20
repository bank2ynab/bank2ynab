---
name: Feature request
about: Suggest an idea for this project

---

*Dear submitter, please edit the following according to your needs. Thank you!*

**New bank format**
*If you're submitting something else, skip or remove this section and continue below.*
- Full name of the bank: ...
- Country (2-character country code): ...
- Any special requirements: ...

*Bank format: only fill out these lines if you're comfortable with it, otherwise skip:*
*To be filled in as required. Delete fields that match default values.*
```
Source Filename Pattern = my_export_filename
Source Filename Extension = .csv
Use Regex for Filename = False
Source CSV Delimiter = ,
Header Rows = 1
Footer Rows = 0
Input Columns = Date,Payee,Outflow,Inflow,Running Balance
Date Format =
# (see http://strftime.org/ for date format strings)
Inflow or Outflow Indicator =
Output Columns = Date,Payee,Category,Memo,Outflow,Inflow
Output Filename Prefix = fixed_
Plugin =
```

**Other feature request**

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
