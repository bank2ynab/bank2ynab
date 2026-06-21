import importlib
import logging
import os
import traceback
from os import path
from typing import Any, Protocol, runtime_checkable

from . import dataframe_handler, transactionfile_reader
from .config_handler import BankConfig
from .dataframe_handler import CSVTransactionSource, DataframeHandler


@runtime_checkable
class BankPlugin(Protocol):
    """Protocol that every plugin-loaded bank handler must satisfy.

    ``build_bank()`` in a plugin module returns a ``BankHandler`` subclass;
    at load time ``bank_handler.build_bank()`` validates the returned object
    against this Protocol so failures surface immediately rather than at
    first use.
    """

    def _preprocess_file(self, file_path: str, plugin_args: list[Any]) -> str: ...


# TODO - there's a lot of overlap between BankHandler and BankConfig,
# review the division of responsibilities and refactor if necessary
class BankHandler:
    """Handle the flow for data input, parsing, and data output for a given bank configuration."""

    def __init__(self, config: BankConfig) -> None:
        """Initialise object and load bank-specific configuration parameters.

        Args:
            config: Bank configuration parameters.
        """
        self.name = config.bank_name
        self.config = config
        self.files_processed = 0
        self.transaction_list: list[dict] = list()

    def run(self) -> None:
        matching_files = transactionfile_reader.get_files(
            name=self.config.bank_name,
            file_pattern=self.config.input_filename,
            try_path=self.config.path,
            regex_active=self.config.regex,
            ext=self.config.ext,
            prefix=self.config.fixed_prefix,
        )

        file_dfs: list = list()

        for src_file in matching_files:
            logging.info(f"\nParsing input file: {src_file} ({self.name})")
            try:
                # perform preprocessing operations on file if required
                src_file = self._preprocess_file(
                    file_path=src_file,
                    plugin_args=self.config.plugin_args,
                )
                # get file's encoding
                src_encod = transactionfile_reader.detect_encoding(src_file)
                # create our base dataframe

                source = CSVTransactionSource(
                    file_path=src_file,
                    delim=self.config.input_delimiter,
                    header_rows=self.config.header_rows,
                    footer_rows=self.config.footer_rows,
                    encod=src_encod,
                )
                df_handler = DataframeHandler()
                df_handler.run(source=source, config=self.config)

                self.files_processed += 1
            except ValueError as e:
                logging.info(f"No output data from this file for this bank. ({e})")
                logging.debug(traceback.format_exc())
            else:
                # make sure our data is not blank before writing
                if not df_handler.df.empty:
                    # only save a file if required
                    if self.config.save_output is True:
                        # write export file
                        output_path = get_output_path(
                            input_path=src_file,
                            prefix=self.config.fixed_prefix,
                            ext=self.config.output_ext,
                        )
                        logging.info(f"Writing output file: {output_path}")
                        df_handler.output_csv(output_path)
                    # save api transaction data for each bank to list
                    file_dfs.append(df_handler.api_transaction_df)
                    # delete original csv file
                    if self.config.delete_original is True:
                        logging.info(f"Removing input file: {src_file}")
                        os.remove(src_file)
                else:
                    logging.info("No output data from this file for this bank.")
        # don't add empty transaction dataframes
        if file_dfs:
            combined_df = dataframe_handler.combine_dfs(file_dfs)
            self.transaction_list = combined_df.to_dict(orient="records")

    def _preprocess_file(self, file_path: str, plugin_args: list[Any]) -> str:
        """Pre-process a file before reading (used by plugins for unusual formats).

        Args:
            file_path: Path to file.
            plugin_args: Plugin-specific arguments.

        Returns:
            str: Path to the (possibly modified) file.
        """
        # intentionally empty - plugins can use this function
        return file_path


def get_output_path(input_path: str, prefix: str, ext: str) -> str:
    """Generate the name of the output file.

    Args:
        input_path: Path to the input file.
        prefix: Prefix to add to the output filename.
        ext: Extension for the output file.

    Returns:
        str: Target filename for the output file.
    """
    target_dir = path.dirname(input_path)
    target_fname = path.basename(input_path)[:-4]

    new_filename = f"{prefix}{target_fname}{ext}"
    new_path = path.join(target_dir, new_filename)
    counter = 1
    while path.isfile(new_path):
        new_filename = f"{prefix}{target_fname}_{counter}{ext}"
        new_path = path.join(target_dir, new_filename)
        counter += 1
    return new_path


def build_bank(bank_config: BankConfig) -> BankHandler:
    """Load the correct bank handler class for a given configuration.

    Args:
        bank_config: Bank configuration parameters.

    Returns:
        BankHandler: Bank handler instance for the given configuration.

    Raises:
        ImportError: If the specified plugin does not contain a build_bank method.
    """
    plugin_module_name = bank_config.plugin or None
    if plugin_module_name:
        module = importlib.import_module(f".plugins.{plugin_module_name}", package="bank2ynab")
        if not hasattr(module, "build_bank"):
            raise ImportError(
                f"The specified plugin {plugin_module_name}.py "
                "does not contain the required build_bank(config) method."
            )
        bank = module.build_bank(bank_config)
        if not isinstance(bank, BankPlugin):
            raise ImportError(
                f"Plugin {plugin_module_name} returned an object that does "
                "not implement the BankPlugin protocol "
                "(_preprocess_file is required)."
            )
        return bank
    else:
        return BankHandler(config=bank_config)
