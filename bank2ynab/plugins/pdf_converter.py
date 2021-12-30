import logging

import pandas as pd
import pdfplumber
from bank_handler import BankHandler, get_output_path


class PDF_Converter(BankHandler):
    def __init__(self, config_object):
        """
        :param config_object: a dictionary of conf parameters
        """
        super(PDF_Converter, self).__init__(config_object)
        self.config = config_object

    def _preprocess_file(self, file_path: str, plugin_args: list) -> str:
        logging.info("Converting PDF file...")
        # generate output path
        new_path = get_output_path(
            input_path=file_path,
            prefix=f"Converted PDF_{self.config['bank_name']}_",
            ext=".csv",
        )
        # create the pdf object
        pdf = pdfplumber.open(file_path)
        # create empty dataframe
        column_labels = self.config["input_columns"]
        combined_df = pd.DataFrame(columns=column_labels)
        # add each page's main table to the dataframe
        for page in pdf.pages:

            table = page.extract_table()
            try:
                # get the main table for a page & set columns
                page_df = pd.DataFrame(table, columns=column_labels)
                # if the table has values, add it to the dataframe
                if not page_df.empty:
                    combined_df = combined_df.append(
                        page_df, ignore_index=True
                    )
            except ValueError:
                # if the number of columns isn't right, ignore the table
                pass
        # write the dataframe to output file
        combined_df.to_csv(new_path, index=False)
        logging.info("\tFinished converting PDF file.")
        # return the path the the output file
        return new_path


def build_bank(config):
    """This factory function is called from the main program,
    and expected to return a B2YBank subclass.
    Without this, the module will fail to load properly.

    :param config: dict containing all available configuration parameters
    :return: a B2YBank subclass instance
    """
    return PDF_Converter(config)
