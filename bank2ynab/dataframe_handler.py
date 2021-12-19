import logging

import pandas as pd


class DataframeHandler:
    # TODO - integrate payee mapping in this class

    """
    use the details for a specified config to produce a cleaned dataframe
    matching a given specification
    """

    def __init__(
        self,
        *,
        file_path: str,
        delim: str,
        header_rows: int,
        footer_rows: int,
        encod: str,
        input_columns: list,
        output_columns: list,
        api_columns: list,
        cd_flags: list,
        date_format: str,
        fill_memo: bool,
        currency_fix: float,
    ) -> None:
        """
        initialise cleaner object using provided dataframe and parameters

        :param df: dataframe to be modified
        :type df: DataFrame
        :param input_columns: columns present in input data
        :type input_columns: list
        :param output_columns: desired columns to be present in output data
        :type output_columns: list
        :param api_columns: desired columns to be present in api data
        :type api_columns: list
        :param cd_flags: parameter to indicate inflow/outflow for a row
        :type cd_flags: list
        :param date_format: string format for date
        :type date_format: str
        :param fill_memo: switch whether to fill blank memo with payee data
        :type fill_memo: bool
        :param currency_fix: value to divide all currency amounts by
        :type currency_fix: float
        """
        self.input_columns = input_columns
        self.output_columns = output_columns
        self.api_columns = api_columns
        self.cd_flags = cd_flags
        self.date_format = date_format
        self.fill_memo = fill_memo
        self.currency_fix = currency_fix

        self.df = pd.read_csv(
            file_path,
            delimiter=delim,
            skipinitialspace=True,  # skip space after delimiter
            names=[],  # don't set column headers initially
            skiprows=header_rows,  # skip header rows
            skipfooter=footer_rows,  # skip footer rows
            skip_blank_lines=True,  # skip blank lines
            encoding=encod,
            memory_map=True,  # access file object directly - no I/O overhead
            engine="python",
        )

    def parse_data(self) -> None:
        """
        convert each column of the dataframe to match ideal output data

        :return: modified dataframe matching provided configuration values
        :rtype: DataFrame
        """
        # set column names based on input column list
        self.df.columns = self.input_columns

        # debug to see what our df is like before transformation
        logging.debug(f"\nInitial DF\n{self.df.head()}")

        # merge duplicate input columns
        self._merge_duplicate_columns(self.input_columns)
        # add missing columns
        self._add_missing_columns(
            self.input_columns, self.output_columns + self.api_columns
        )
        # fix date format
        self.df["Date"] = self._fix_date(self.df["Date"], self.date_format)
        # process Inflow/Outflow flags
        self._cd_flag_process(self.cd_flags)
        # fix amounts (convert negative inflows and outflows etc)
        self._fix_amount()
        # auto fill memo from payee if required
        self._auto_memo(self.fill_memo)
        # auto fill payee from memo
        self._auto_payee()
        # remove invalid rows
        self._remove_invalid_rows()
        # fill API-specific columns
        self.fill_api_columns()
        # set final columns & order for output file
        self.output_df = self.df[self.output_columns]
        # display parsed line count
        logging.info(f"Parsed {self.df.shape[0]} lines")
        # view final dataframe # TODO - switch to debug once finished here
        logging.debug(f"\nFinal DF\n{self.df.head(10)}")
        # check if dataframe is empty
        self.empty = self.df.empty

    def _merge_duplicate_columns(self, input_columns: list) -> None:
        """
        Merges columns specified more than once in the input_columns list.
        Note: converts values into strings before merging.

        :param input_columns: the list of columns in the input file
        :type input_columns: list
        :return: None
        """

        # create dictionary mapping column names to indices of duplicates
        cols_to_merge = dict()
        for index, col in enumerate(input_columns):
            if col not in cols_to_merge:
                cols_to_merge[col] = []
            cols_to_merge[col] += [index]

        # go through each key
        for key in cols_to_merge:
            key_cols = cols_to_merge[key]
            if len(key_cols) > 1:
                # change first column to string
                self.df.iloc[:, key_cols[0]] = (
                    self.df.iloc[:, key_cols[0]].astype(str) + " "
                )
                # merge every duplicate column into the 1st instance
                # of the column name
                for dupe_count, key_col in enumerate(key_cols[1:]):
                    # add string version of each column onto the first column
                    self.df.iloc[
                        :, key_cols[0]
                    ] += f"{self.df.iloc[:, key_col]} "
                    # rename duplicate column
                    self.df.columns.values[key_col] = f"{key} {dupe_count}"
                # remove excess spaces
                self.df[key] = (
                    self.df[key]
                    .str.replace("\\s{2,}", " ", regex=True)
                    .str.strip()
                )

        logging.debug(f"\nAfter duplicate merge\n{self.df.head()}")

    def _add_missing_columns(
        self, input_cols: list, output_cols: list
    ) -> None:
        """
        Adds any missing required columns to the Dataframe.

        :param input_columns: the list of columns in the input file
        :type input_columns: list
        :param output_columns: the desired list of columns as output
        :type output_columns: list
        :return: None
        """
        # compare input & output column lists to find missing columns
        missing_cols = list(set(output_cols).difference(input_cols))
        # add missing output columns
        for col in missing_cols:
            self.df.insert(loc=0, column=col, value="")
            self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
        logging.debug(f"\nAfter adding missing columns:\n{self.df.head()}")

    def _cd_flag_process(self, cd_flags: list) -> None:
        """
        fix columns where inflow/outflow is indicated by a flag
        in a separate column
        the cd_flag list is in the form
        "indicator column, outflow flag, inflow flag"
        (the code does not use the indicator flag specified in the flag list,
        but instead the "CDFlag" column specified in Input Columns)

        :param cd_flags: list of parameters for applying indicators
        :type cd_flags: list
        :return: None
        """
        if len(cd_flags) == 3:
            outflow_flag = cd_flags[2]
            # if this row is indicated to be outflow, make inflow negative
            self.df.loc[
                self.df["CDFlag"] is outflow_flag, ["Inflow"]
            ] = "-{}".format(self.df["Inflow"])

    def _fix_amount(self) -> None:
        """
        fix currency string formatting
        convert currency values to floats
        convert negative inflows into outflows and vice versa

        :return: None
        """
        # fix various formatting issues
        self.df["Inflow"] = self._clean_monetary_values(self.df["Inflow"])
        self.df["Outflow"] = self._clean_monetary_values(self.df["Outflow"])

        # negative inflow = outflow
        self.df.loc[self.df["Inflow"] < 0, ["Outflow"]] = (
            self.df["Inflow"] * -1
        )
        self.df.loc[self.df["Inflow"] < 0, ["Inflow"]] = 0

        # negative outflow = inflow
        self.df.loc[self.df["Outflow"] < 0, ["Inflow"]] = (
            self.df["Outflow"] * -1
        )
        self.df.loc[self.df["Outflow"] < 0, ["Outflow"]] = 0

        # create amount column for API (in milliunits)
        self.df["amount"] = 1000 * (self.df["Inflow"] - self.df["Outflow"])

    def _clean_monetary_values(self, num_series: pd.Series) -> pd.Series:
        """
        convert "," to "." then remove every instance of . except last one
        remove any characters from inflow or outflow strings except
        digits, "-", and "."
        fill in null values with 0

        :param num_series: series of values to modify
        :type num_series: Series
        :return: modified series
        :rtype: Series
        """
        # convert all commas to full stops
        num_series.replace({"\\,": "."}, regex=True, inplace=True)
        # remove all except last decimal point
        num_series.replace({"\\.(?=.*?\\.)": ""}, regex=True, inplace=True)
        # remove all non-digit characters
        num_series.replace(
            {
                "[^\\d\\.-]": "",
            },
            regex=True,
            inplace=True,
        )
        # fill in null values with 0
        num_series.fillna(value=0, inplace=True)
        # currency conversion if multiplier specified
        num_series = num_series.astype(float) / self.currency_fix
        return num_series.astype(float)

    def _remove_invalid_rows(self) -> None:
        """
        Removes invalid rows from dataframe.
        An invalid row is one which does not have a date
        or one without an Inflow or Outflow value.

        :return: None
        """
        # filter out rows where Inflow and Outflow are both blank
        self.df.query("Inflow.notna() & Outflow.notna()", inplace=True)
        # filter rows with an invalid date
        self.df.query("Date.notna()", inplace=True)
        self.df.reset_index(inplace=True)

    def _auto_memo(self, fill_memo: bool) -> None:
        """
        if memo is blank, fill with contents of payee column

        :param fill_memo: boolean to check
        :type fill_memo: bool
        :return: None
        """
        if fill_memo:
            self.df["Memo"].fillna(self.df["Payee"], inplace=True)

    def _auto_payee(self) -> None:
        """
        if Payee is blank, fill with contents of Memo column

        :return: None
        """
        self.df["Payee"].fillna(self.df["Memo"], inplace=True)

    def _fix_date(self, date_series: pd.Series, date_format: str) -> pd.Series:
        """
        If provided with an input date format,
        process the date column to the ISO format.
        Any non-parseable dates are returned as a NaT null value

        :param df: dataframe to modify
        :type df: Series
        :param date_format: date format codes according to 1989 C standard
        (https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
        :type date_format: str
        :return: modified dataframe
        :rtype: Series
        """
        date_series = pd.to_datetime(
            date_series,
            format=date_format,
            infer_datetime_format=True,
            errors="coerce",
        )

        logging.debug("\nFixed dates:\n{}".format(date_series.head()))

        return date_series

    def output_csv(self, path: str) -> None:
        """
        Writes self.df to the specified filepath as a csv file

        :param path: path to write exported file to
        :type path: str
        """
        self.output_df.to_csv(path, index=False)

    def fill_api_columns(
        self,
    ) -> None:  # TODO handle account ID
        self.df["account_id"] = "NOT YET IMPLEMENTED"  # TODO
        self.df["date"] = self.df["Date"]
        self.df["payee_name"] = self.df["Payee"[:50]]
        self.df["memo"] = self.df["Memo"[:100]]
        self.df["category"] = ""
        self.df["cleared"] = "cleared"
        self.df["payee_id"] = None
        self.df["category_id"] = None
        self.df["approved"] = False
        self.df["flag_color"] = None

        # import_id format = YNAB:amount:ISO-date:occurrences
        # Maximum 36 characters ("YNAB" + ISO-date = 10 characters)
        self.df["import_id"] = self.df.agg(
            lambda x: f"{x['amount']}:{x['date']}:", axis=1
        )
        # count every instance of import id & add a counter to id
        self.df["same_id_count"] = (
            self.df.groupby(["import_id"]).cumcount() + 1
        ).astype(str)
        self.df["import_id"] = self.df["import_id"] + self.df["same_id_count"]
        # move import_id to the end
        cols = list(self.df.columns.values)
        cols.pop(cols.index("import_id"))
        self.df = self.df[cols + ["import_id"]]
        # view dataframe
        logging.debug(f"\nAfter API column processing\n{self.df.head()}")

        """
        # assign values to transaction dictionary
        transaction = {
            "account_id": account_id,
            "date": date,
            "payee_name": payee[:50],
            "amount": amount,
            "memo": memo[:100],
            "category": category,
            "cleared": "cleared",
            "import_id": self.create_import_id(amount, date, transactions),
            "payee_id": None,
            "category_id": None,
            "approved": False,
            "flag_color": None,
        }
        """
