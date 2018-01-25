# with thanks to https://github.com/jpsk/Swedbank-to-YNAB4-converter/

from bank2ynab import B2YBank, CrossversionCsvReader

class NLRabobankPlugin(B2YBank):
    def __init__(self, config_object, is_py2):
        super(NLRabobankPlugin, self).__init__(config_object, is_py2)
        self.name = "nl-rabobank"

    def read_data(self, file_path):
        delim = self.config["input_delimiter"]
        output_columns = self.config["output_columns"]
        # we know it should have headers, but we respect the setting
        header_rows = self.config["header_rows"]
        footer_rows = self.config["footer_rows"]
        output_data = []

        with CrossversionCsvReader(file_path,
                                   self._is_py2,
                                   delimiter=delim) as reader:
            for index, row in enumerate(reader):
                # skip first row if headers
                if index == 0 and header_rows != 0:
                    continue
                tmp = {}
                """
                I assume that "[2]" means "field 2 in the current row".
                DATE STUFF:
                YNAB's date format is "DD/MM/YYYY". 
                This bank's date format is "YYYMMDD" without delimiters.
                Moving the substrings into the proper order: https://stackoverflow.com/a/663175/20571
                """
                date = row[2]
                tmp["Date"] = date[6:7] + '/' + date[4:5] + '/' + date[0:3]
                # PAYEE STUFF:
                tmp["Payee"] = row[7]
                # CATEGORY STUFF:
                tmp["Category"] = ''
                # MEMO STUFF:
                tmp["Memo"] = row[11]
                # AMOUNT STUFF:
                # C means inflow (credit), D means outflow (debit)
                if row[4] == 'C':
                    tmp["Outflow"] = ''
                    tmp["Inflow"] = row[5]
                else:
                    tmp["Outflow"] = row[5]
                    tmp["Inflow"] = ''

                # respect Output Columns option
                out_row = [''] * len(output_columns)
                for index, key in enumerate(output_columns):
                    out_row[index] = tmp.get(key, "")
                output_data.append(out_row)
        return output_data


def build_bank(config, is_py2):
    return NLRabobankPlugin(config, is_py2)
