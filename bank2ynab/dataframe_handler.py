import logging

import pandas as pd


class DataframeHandler:
    # TODO - integrate payee mapping in this class

    """
    use the details for a specified config to produce a cleaned dataframe
    matching a given specification
    """

    def __init__(self) -> None:
        pass

    def output_csv(self, path: str) -> None:
        """
        Writes df to the specified filepath as a csv file

        :param path: path to write exported file to
        :type path: str
        """
        self.output_df.to_csv(path, index=False)

    def run(
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
        date_dedupe: bool,
        fill_memo: bool,
        currency_fix: float,
    ) -> None:
        """
        Complete handling of Dataframe creation & output.

        :param df: dataframe to be modified
        :type df: DataFrame
        :param file_path: Path to CSV file
        :type file_path: str
        :param delim: CSV separator
        :type delim: str
        :param header_rows: Number of header rows
        :type header_rows: int
        :param footer_rows: Number of footer rows
        :type footer_rows: int
        :param encod: CSV file encoding
        :type encod: str
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
        :param date_dedupe: whether to fill in date with previous if blank
        :type date_dedupe: bool
        :param fill_memo: switch whether to fill blank memo with payee data
        :type fill_memo: bool
        :param currency_fix: value to divide all currency amounts by
        :type currency_fix: float
        """
        # read data from input file to dataframe
        self.df = read_csv(
            file_path=file_path,
            delim=delim,
            header_rows=header_rows,
            footer_rows=footer_rows,
            encod=encod,
        )
        # modify dataframe to match desired output
        self.df = parse_data(
            df=self.df,
            input_columns=input_columns,
            output_columns=output_columns,
            api_columns=api_columns,
            cd_flags=cd_flags,
            date_format=date_format,
            date_dedupe=date_dedupe,
            fill_memo=fill_memo,
            currency_fix=currency_fix,
        )
        # check if dataframe is empty
        self.empty = self.df.empty
        # set final columns & order for output file
        self.output_df = self.df[output_columns]
        # set json output
        self.api_transaction_data = output_json_transactions(
            self.df[api_columns]
        )


def read_csv(
    file_path: str,
    delim: str,
    header_rows: int,
    footer_rows: int,
    encod: str,
) -> pd.DataFrame:
    """
    Read a specified CSV file into a Dataframe.

    :param file_path: Path to CSV file
    :type file_path: str
    :param delim: CSV separator
    :type delim: str
    :param header_rows: Number of header rows
    :type header_rows: int
    :param footer_rows: Number of footer rows
    :type footer_rows: int
    :param encod: CSV file encoding
    :type encod: str
    :return: Dataframe read from CSV file
    :rtype: pd.DataFrame
    """
    df = pd.read_csv(
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
    return df


def parse_data(
    *,
    df: pd.DataFrame,
    input_columns: list,
    output_columns: list,
    api_columns: list,
    cd_flags: list,
    date_format: str,
    date_dedupe: bool,
    fill_memo: bool,
    currency_fix: float,
) -> pd.DataFrame:
    """
    Convert each column of the dataframe to match ideal output data

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
    :param date_dedupe: whether to fill in date with previous if blank
    :type date_dedupe: bool
    :param fill_memo: switch whether to fill blank memo with payee data
    :type fill_memo: bool
    :param currency_fix: value to divide all currency amounts by
    :type currency_fix: float
    :return: modified dataframe matching provided configuration values
    :rtype: DataFrame
    """
    # set column names based on input column list
    df.columns = input_columns
    # debug to see what our df is like before transformation
    logging.debug(f"\nInitial DF\n{df.head()}")
    # merge duplicate input columns
    merge_duplicate_columns(df, input_columns)
    # add missing columns
    add_missing_columns(df, input_columns, output_columns + api_columns)
    # fix date format
    df["Date"] = fix_date(df["Date"], date_format)
    df["Date"] = fill_empty_dates(df["Date"], date_dedupe)
    # fix inflow/outflow string formatting
    df["Inflow"] = clean_monetary_values(df["Inflow"])
    df["Outflow"] = clean_monetary_values(df["Outflow"])
    # process Inflow/Outflow flags
    df = cd_flag_process(df, cd_flags)
    # fix amounts (convert negative inflows and outflows etc)
    df = fix_amount(df, currency_fix)
    # auto fill memo from payee if required
    df = auto_memo(df, fill_memo)
    # auto fill payee from memo
    df = auto_payee(df)
    # remove invalid rows
    df = remove_invalid_rows(df)
    # fill API-specific columns
    df = fill_api_columns(df)
    # remove invalid rows
    df = remove_invalid_rows(df)
    # display parsed line count
    logging.info(f"Parsed {df.shape[0]} lines")
    # view final dataframe
    logging.debug(f"\nFinal DF\n{df.head(10)}")

    return df


def merge_duplicate_columns(
    df: pd.DataFrame, input_columns: list[str]
) -> pd.DataFrame:
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
            df.iloc[:, key_cols[0]] = df.iloc[:, key_cols[0]].astype(str) + " "
            # merge every duplicate column into the 1st instance
            # of the column name
            for dupe_count, key_col in enumerate(key_cols[1:]):
                # add string version of each column onto the first column
                df.iloc[:, key_cols[0]] += f"{df.iloc[:, key_col]} "
                # rename duplicate column
                df.columns.values[key_col] = f"{key} {dupe_count}"
            # remove excess spaces
            df[key] = (
                df[key].str.replace("\\s{2,}", " ", regex=True).str.strip()
            )

    logging.debug(f"\nAfter duplicate merge\n{df.head()}")
    return df


def add_missing_columns(
    df: pd.DataFrame, input_cols: list[str], output_cols: list[str]
) -> pd.DataFrame:
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
        df.insert(loc=0, column=col, value="")
        df[col] = pd.to_numeric(df[col], errors="coerce")
    logging.debug(f"\nAfter adding missing columns:\n{df.head()}")
    return df


def cd_flag_process(df: pd.DataFrame, cd_flags: list) -> pd.DataFrame:
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
        df.loc[df["CDFlag"] == outflow_flag, ["Inflow"]] = -1 * df["Inflow"]
    return df


def fix_amount(df: pd.DataFrame, currency_fix: float) -> pd.DataFrame:
    """
    fix currency string formatting
    convert currency values to floats
    convert negative inflows into outflows and vice versa

    :return: None
    """
    # negative inflow = outflow
    df.loc[df["Inflow"] < 0, ["Outflow"]] = df["Inflow"] * -1
    df.loc[df["Inflow"] < 0, ["Inflow"]] = 0

    # negative outflow = inflow
    df.loc[df["Outflow"] < 0, ["Inflow"]] = df["Outflow"] * -1
    df.loc[df["Outflow"] < 0, ["Outflow"]] = 0

    # currency conversion if multiplier specified
    df["Inflow"] = df["Inflow"] / currency_fix
    df["Outflow"] = df["Outflow"] / currency_fix

    # create amount column for API (in milliunits)
    df["amount"] = 1000 * (df["Inflow"] - df["Outflow"])
    return df


def clean_monetary_values(num_series: pd.Series) -> pd.Series:
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
    return num_series.astype(float)


def remove_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes invalid rows from dataframe.
    An invalid row is one which does not have a date
    or one without an Inflow or Outflow value.

    :param df: dataframe to modify
    :type df: pd.DataFrame
    :return: pd.DataFrame
    """
    # filter out rows where Inflow and Outflow are both blank
    df.query("Inflow.notna() | Outflow.notna()", inplace=True)
    # filter rows with an invalid date
    df.query("Date.notna()", inplace=True)
    df.fillna(0, inplace=True)
    df.query("amount!=0", inplace=True)
    df.reset_index(inplace=True)
    return df


def auto_memo(df: pd.DataFrame, fill_memo: bool) -> pd.DataFrame:
    """
    If memo is blank, fill with contents of payee column.

    :param df: dataframe to modify
    :type df: pd.DataFrame
    :param fill_memo: boolean to check
    :type fill_memo: bool
    :return: modified dataframe
    :rtype: pd.DataFrame
    """
    # TODO - fix empty strings
    if fill_memo:
        df["Memo"].fillna(df["Payee"], inplace=True)
    return df


def auto_payee(df: pd.DataFrame) -> pd.DataFrame:
    """
    if Payee is blank, fill with contents of Memo column

    :return: None
    """
    df["Payee"].fillna(df["Memo"], inplace=True)
    return df


def fix_date(date_series: pd.Series, date_format: str) -> pd.Series:
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

    return date_series.dt.strftime("%Y-%m-%d")


def fill_empty_dates(date_series: pd.Series, fill_dates: bool) -> pd.Series:
    """
    Fill in empty dates with values from previous cells.

    :param date_series: data series to modify
    :type date_series: pd.Series
    :param fill_dates: whether to fill in empty dates or not
    :type fill_dates: bool
    :return: modified data series
    :rtype: pd.Series
    """
    if fill_dates:
        date_series[date_series == ""] = pd.NA
        date_series.fillna(method="ffill", inplace=True)  # type:ignore

    return date_series


def fill_api_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:  # TODO handle account ID
    df["account_id"] = ""  # TODO - not yet implemented
    df["date"] = df["Date"].astype(str)
    df["payee_name"] = df["Payee"].str.slice(0, 50)
    df["memo"] = df["Memo"].str.slice(0, 100)
    df["category"] = ""
    df["cleared"] = "cleared"
    df["payee_id"] = None
    df["category_id"] = None
    df["approved"] = False
    df["flag_color"] = None

    # import_id format = YNAB:amount:ISO-date:occurrences
    # Maximum 36 characters ("YNAB" + ISO-date = 10 characters)
    df["import_id"] = df.agg(
        lambda x: f"YNAB:{x['amount']}:{x['date']}:", axis=1
    )
    # count every instance of import id & add a counter to id
    df["same_id_count"] = (df.groupby(["import_id"]).cumcount() + 1).astype(
        str
    )
    df["import_id"] = df["import_id"] + df["same_id_count"]
    # move import_id to the end
    cols = list(df.columns.values)
    cols.pop(cols.index("import_id"))
    df = df[cols + ["import_id"]]
    # view dataframe
    logging.debug(f"\nAfter API column processing\n{df.head()}")
    return df


def output_json_transactions(
    df: pd.DataFrame,
) -> dict[str, str]:

    return {"transactions": df.to_json(orient="records")}
