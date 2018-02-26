# Package meta-data:
NAME = "bank2ynab"
DESCRIPTION = "A common project to consolidate all conversion efforts from various banks' export formats into YNAB's import format."
LONG_DESCRIPTION = "A common project to consolidate all conversion efforts from various banks' export formats into YNAB's import format."
URL = "https://github.com/torbengb/bank2ynab"
EMAIL = "torben@g-b.dk"
AUTHOR = "https://github.com/torbengb/bank2ynab/graphs/contributors"

# define the version numbers:
version_major = 1  # must be integer
version_minor = 1  # must be integer
version_patch = "0"  # must be string
# I'd like to *automagically* include the GitHub branch here:
version_suffix = "mytestbranch"  

# proper release should not have a version suffix:
if version_suffix == "master": 
    version_suffix = ""
# if it's not a master release then add the suffix to the patch level:
if version_suffix != "": 
    version_patch = version_patch + '-' + version_suffix

# version number according to https://codereview.stackexchange.com/a/131490 :
version_info = (version_major, version_minor, version_patch)
VERSION = '.'.join(str(c) for c in version_info)
