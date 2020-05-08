"""
Helper script to update README.md to reflect banks listed in bank2ynab.conf
"""

import re

def get_banks(file):
    """
    :param file: filename for config file
    :return banks: list of bank names
    """
    with open(file, "r") as f:
        file_contents = f.read()    
    
    bracket_regex = re.compile("\n\[(.*)\]\n")
    banks = bracket_regex.findall(file_contents)
    
    return banks[1:]
# Variables
config_file = "bank2ynab.conf"
readme_file = "README.md"
start_token = "<!--AUTO BANK UPDATE START-->"
end_token = "<!--AUTO BANK UPDATE END-->"
run(config_file, readme_file, start_token, end_token)
