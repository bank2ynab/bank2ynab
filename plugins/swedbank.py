# with thanks to https://github.com/jpsk/Swedbank-to-YNAB4-converter/
from bank2ynab import B2YBank, CrossversionCsvReader


class SwedbankPlugin(B2YBank):
    def read_data(self, file_path):
        delim = self.config["input_delimiter"]
        output_columns = self.config["output_columns"]
        output_data = []

        with CrossversionCsvReader(file_path,
                                   self._is_py2,
                                   delimiter=delim) as reader:
            for row in reader:
                tmp = {}
                date = row[2].split('-')
                tmp["Date"] = date[0] + '/' + date[1] + '/' + date[2]
                tmp["Payee"] = ''  # wat?
                tmp["Category"] = ''
                tmp["Memo"] = row[4]  # this is probably the payee...
                if row[7] == 'K':
                    tmp["Outflow"] = ''
                    tmp["Inflow"] = row[5]
                else:
                    tmp["Outflow"] = row[5]
                    tmp["Inflow"] = ''

                # respect Output Columns option
                out_row = []
                for index, key in enumerate(output_columns):
                    out_row[key] = tmp.get(key, "")
                output_data.append(out_row)
        return output_data


def build_bank(config, is_py2):
    return SwedbankPlugin(config, is_py2)
