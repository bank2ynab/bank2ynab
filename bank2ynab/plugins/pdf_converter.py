import logging

import pandas as pd
import pdfplumber

logging.getLogger("pdfplumber").setLevel(logging.WARNING)
logging.getLogger("pdfminer").setLevel(logging.WARNING)

from .. import bank_handler
from ..bank_handler import BankHandler
from ..config_handler import BankConfig


class PDF_Converter(BankHandler):
    def __init__(self, bank_config: BankConfig) -> None:
        """Initialise PDF converter with bank configuration.

        Args:
            bank_config: A BankConfig instance containing conf parameters.
        """
        super().__init__(bank_config)
        self.config = bank_config

    def _preprocess_file(self, file_path: str, plugin_args: list) -> str:
        """Combine all tables in a PDF file into one table and write to CSV.

        Args:
            file_path: Path to PDF file.
            plugin_args: Plugin arguments (unused in this plugin).

        Returns:
            str: Path to CSV file.
        """
        logging.info("Converting PDF file...")

        # create dataframe from pdf
        df = read_pdf_to_dataframe(pdf_path=file_path, table_cols=self.config.input_columns)
        # generate output path
        new_path = bank_handler.get_output_path(
            input_path=file_path,
            prefix=f"Converted PDF_{self.config.bank_name}_",
            ext=".csv",
        )
        # write the dataframe to output file
        df.to_csv(new_path, index=False)
        logging.info("\tFinished converting PDF file.")
        return new_path


def read_pdf_to_dataframe(pdf_path: str, table_cols: list[str]) -> pd.DataFrame:
    """Read the main table from each page of a PDF and combine into a single dataframe.

    Tables with the wrong number of columns are ignored.

    Args:
        pdf_path: Filepath for PDF file.
        table_cols: Columns to use for dataframe.

    Returns:
        pd.DataFrame: Dataframe of combined tables.
    """
    # TODO - fix excessive text output from pdfplumber
    # create the pdf object
    pdf = pdfplumber.open(pdf_path)
    # create empty dataframe
    combined_df = pd.DataFrame(columns=table_cols)
    # add each page's main table to the dataframe
    dfs_to_add = list()
    for page in pdf.pages:
        table = page.extract_table()

        try:
            # get the main table for a page & set column names
            page_df = pd.DataFrame(table, columns=table_cols)
            # if the table has values, add it to the dataframe
            if not page_df.empty:
                dfs_to_add.append(page_df)
        except ValueError:
            # if the number of columns isn't right, ignore the table
            pass
    # combine all the tables into one dataframe
    if dfs_to_add:
        # combine all the tables into one dataframe
        combined_df = pd.concat(dfs_to_add, ignore_index=True)
    return combined_df


def build_bank(config) -> PDF_Converter:
    """Return a PDF_Converter instance for a given bank configuration.

    Args:
        config: A BankConfig instance containing conf parameters.

    Returns:
        PDF_Converter: A BankHandler subclass instance.
    """
    return PDF_Converter(config)
