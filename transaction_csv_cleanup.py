#! /usr/bin/python
# transaction_csv_cleanup.py
# for Python 3

# Searches specified folder or default download folder for exported
# bank transaction file (.csv format) & adjusts format for YNAB import

# CHANGELOG
# 2017-09-29
#   ~ Merged in parameters from https://www.reddit.com/user/FinibusBonorum
#   ~ Auto folder finder disabled if folder path specified
#   ~ Moved winreg import into Windows-specific section to avoid Linux conflict
#   ~ Refined winreg import
#   ~ Realised that Windows has no default shebang support so just used Linux shebang line!
#   ~ Added fix_row function that handles missing input headers better than previously
#   ~ Renamed find_downloads() to find_directory()
#   ~ Added header_swap function
# 2017-10-04
#   ~ Added g_hasheaders variable for if data is missing column headers
#   ~ Actually implemented csv delimiter in csv function!

# OPERATIONS
#   ~ Find & open TransactionExport.csv for processing
#   ~ Change columns from
#       Date, Details, Debit, Credit, Balance to
#       Date, Payee, Category, Memo, Outflow, Inflow & delete Balance column
#   ~ Create blank Category column
#   ~ Copy data from Payee column into Memo column
#   ~ Write new data to [g_filepath]+[g_filename]+[g_suffix] = fixed_TransactionExport.csv

# edit the following section based on bank format
g_filename = "TransactionExport"
g_input_columns = ["Date", "Payee", "Outflow", "Inflow", "Running Balance"]
g_output_columns = ["Date", "Payee", "Category", "Memo", "Outflow", "Inflow"]
g_filepath = ""
g_suffix = ".csv"
g_fixed_prefix = "fixed_"
g_delimiter = ","
g_hasheaders = True
#

# don't edit below here unless you know what you're doing!
import csv, os

def get_files():
    # find the transaction file         
    os.chdir(find_directory())
    a = g_suffix
    b = g_filename
    c = g_fixed_prefix    
    return [f for f in os.listdir(".") if f.endswith(a) if b in f if c not in f]
    
def clean_data(file):
    # extract data from transaction file
    output_data = []
    with open(file) as transaction_file:
        transaction_reader = csv.reader(transaction_file, delimiter = g_delimiter)
        transaction_data = list(transaction_reader)

        # make each row of our new transaction file
        for row in transaction_data:
            # add new row to output list
            output_data.append(fix_row(row))

        # fix column headers
        if g_hasheaders is False:
            output_data.insert(0, g_output_columns)
        else:
            output_data[0] = g_output_columns
    
    return output_data
    
def fix_row(row):
    # fixes a row of our file  
    output = []
    for header in g_output_columns:
        header = header_swap(header)
        try:
            # check to see if our output header exists in input
            index = g_input_columns.index(header)
            cell = row[index]
        except ValueError:
            # header isn't in input, default to blank cell
            cell = ""
        output.append(cell)
    return output
                
def header_swap(header):
    # replaces one column's value with another if required
    if header is "Memo":
        header = "Payee"
    return header
                
def write_data(filename, data):
    # write out the new CSV file    
    with open(g_fixed_prefix + filename, "w", newline = "") as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)
    return
    
def find_directory():
    # finds the downloads folder for the active user if g_filepath is not set
    if g_filepath is "":
        if os.name is "nt":
            # Windows
            from winreg import OpenKey,  QueryValueEx, HKEY_CURRENT_USER # import Windows-specific stuff here
            shell_path = "SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            dl_key = "{374DE290-123F-4565-9164-39C4925E467B}"
            with OpenKey(HKEY_CURRENT_USER, shell_path) as key:
                dir = QueryValueEx(key, dl_key)[0]
        else:
            # Linux
            userhome = os.path.expanduser('~')
            dir = os.path.join(userhome, "Downloads")      
    else:
        dir = g_filepath
    
    return dir
    
def main():
    # find all applicable files
    files = get_files()
    for file in files:
        # create cleaned csv for each file
        output = clean_data(file)
        write_data(file, output)
        # delete original csv file
        os.remove(file)
    return

main()
