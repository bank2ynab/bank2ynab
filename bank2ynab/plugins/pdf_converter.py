import logging

import pandas as pd
import pdfplumber
from bank_handler import BankHandler, get_output_path


class PDF_Converter(BankHandler):
    def __init__(self, config_object: dict):
        """
        :param config_object: a dictionary of conf parameters
        """
        super(PDF_Converter, self).__init__(config_object)
        self.config = config_object

    def _preprocess_file(self, file_path: str, plugin_args: list) -> str:
        """
        Combines all tables in a PDF file into one table and writes to CSV.

        :param file_path: path to PDF file
        :type file_path: str
        :param plugin_args: plugin arguments (unused in this plugin)
        :type plugin_args: list
        :return: path to CSV file
        :rtype: str
        """
        logging.info("Converting PDF file...")

        # create dataframe from pdf
        df = read_pdf_to_dataframe(
            pdf_path=file_path, table_cols=self.config["input_columns"]
        )
        # generate output path
        new_path = get_output_path(
            input_path=file_path,
            prefix=f"Converted PDF_{self.config['bank_name']}_",
            ext=".csv",
        )
        # write the dataframe to output file
        df.to_csv(new_path, index=False)
        logging.info("\tFinished converting PDF file.")
        return new_path


def read_pdf_to_dataframe(
    pdf_path: str, table_cols: list[str]
) -> pd.DataFrame:
    """
    Reads the main table from each page of a PDF and
    combines them into a single dataframe.
    If the table does not have the right number of columns, it is ignored.

    :param pdf_path: filepath for PDF file
    :type pdf_path: str
    :param table_cols: columns to use for dataframe
    :type table_cols: list[str]
    :return: dataframe of combined tables
    :rtype: pd.DataFrame
    """
    # TODO - fix excessive text output from pdfplumber
    # create the pdf object
    pdf = pdfplumber.open(pdf_path)
    # create empty dataframe
    combined_df = pd.DataFrame(columns=table_cols)
    # add each page's main table to the dataframe
    for page in pdf.pages:
        table = page.extract_table()
        try:
            # get the main table for a page & set column names
            page_df = pd.DataFrame(table, columns=table_cols)
            # if the table has values, add it to the dataframe
            if not page_df.empty:
                combined_df = combined_df.append(page_df, ignore_index=True)
        except ValueError:
            # if the number of columns isn't right, ignore the table
            pass
    return combined_df


def build_bank(config):
    """This factory function is called from the main program,
    and expected to return a BankHandler subclass.
    Without this, the module will fail to load properly.

    :param config: dict containing all available configuration parameters
    :return: a BankHandler subclass instance
    """
    return PDF_Converter(config)
