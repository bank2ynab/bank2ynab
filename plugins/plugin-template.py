# Step 1: See https://github.com/torbengb/bank2ynab/wiki/WorkingWithPlugins
# Step 2: Copy this template into a new file.
# Step 3: In all of the below, replace "TemplateBank" with a descriptive name for the actual bank this plugin is for.

from bank2ynab import B2YBank, CrossversionCsvReader

class YourActualBankPlugin(B2YBank):
    def __init__(self, config_object, is_py2):
        super(YourActualBankPlugin, self).__init__(config_object, is_py2)
        self.name = "YourActualBank"

    def read_data(self, file_path):
        delim = self.config["input_delimiter"]
        output_columns = self.config["output_columns"]
        # we know it should have headers, but we respect the setting
        has_headers = self.config["has_headers"]
        output_data = []

        with CrossversionCsvReader(file_path,
                                   self._is_py2,
                                   delimiter=delim) as reader:
            for index, row in enumerate(reader):
                # skip first row if headers
                if index == 0 and has_headers:
                    continue
                tmp = {}
# DATE STUFF:
# YNAB's date format is "DD/MM/YYYY". 
# Use substrings to move date elements into the proper order: https://stackoverflow.com/a/663175/20571
                date = row[9]
# In your own plugin there should be exactly 1 of these lines. Remove the ones you don't need, and edit as needed.
                tmp["Date"] = date[6:7] + '/' + date[4:5] + '/' + date[0:3] # when source format is "YYYYMMDD" without delimiters.
                tmp["Date"] = date[0:1] + '/' + date[2:3] + '/' + date[4:7] # when source format is "DDMMYYYY" without delimiters.
                tmp["Date"] = date[0:1] + '/' + date[3:4] + '/' + date[6:9] # when source format is "DD-MM-YYYY" with delimiters.
# PAYEE STUFF:
                tmp["Payee"] = row[9]
# CATEGORY STUFF:
                tmp["Category"] = ''
# MEMO STUFF:
                tmp["Memo"] = row[9]
# AMOUNT STUFF:
                tmp["Inflow"] = row[9]
                tmp["Outflow"] = row[9]
                # C means inflow (credit), D means outflow (debit)
                if row[10] == 'C':
                    tmp["Outflow"] = ''
                    tmp["Inflow"] = row[9]
                else:
                    tmp["Outflow"] = row[9]
                    tmp["Inflow"] = ''

                # respect Output Columns option
                out_row = [''] * len(output_columns)
                for index, key in enumerate(output_columns):
                    out_row[index] = tmp.get(key, "")
                output_data.append(out_row)
        return output_data

def build_bank(config, is_py2):
    return YourActualBankPlugin(config, is_py2)
