import csv
import logging

import pandas as pd


class DataframeHandler:
    """Use config to produce a cleaned dataframe matching a given specification."""

    def __init__(self) -> None:
        pass

    def output_csv(self, path: str) -> None:
        """Write df to the specified filepath as a csv file.

        Args:
            path: Path to write exported file to.
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
        input_columns: list[str],
        output_columns: list[str],
        api_columns: list[str],
        cd_flags: list[str],
        date_format: str,
        date_dedupe: bool,
        fill_memo: bool,
        currency_fix: float,
        payee_mappings: dict[str, str] | None = None,
        clean_payee: bool = True,
        clean_memo: bool = True,
    ) -> None:
        """Complete handling of Dataframe creation & output.

        Args:
            file_path: Path to CSV file.
            delim: CSV separator.
            header_rows: Number of header rows.
            footer_rows: Number of footer rows.
            encod: CSV file encoding.
            input_columns: Columns present in input data.
            output_columns: Desired columns to be present in output data.
            api_columns: Desired columns to be present in API data.
            cd_flags: Parameter to indicate inflow/outflow for a row.
            date_format: String format for date.
            date_dedupe: Whether to fill in date with previous if blank.
            fill_memo: Whether to fill blank memo with payee data.
            currency_fix: Value to divide all currency amounts by.
            payee_mappings: Dict of raw payee substring → friendly name; omit or pass None for no mapping.
            clean_payee: Whether to apply string cleaning to Payee field.
            clean_memo: Whether to apply string cleaning to Memo field.
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
            payee_mappings=payee_mappings or {},
            clean_payee=clean_payee,
            clean_memo=clean_memo,
        )
        # check if dataframe is empty
        self.empty = self.df.empty
        # set final columns & order for output file
        self.output_df = self.df[output_columns]
        # set final columns & order for api output
        self.api_transaction_df = self.df[api_columns]


def read_csv(
    file_path: str,
    delim: str,
    header_rows: int,
    footer_rows: int,
    encod: str,
) -> pd.DataFrame:
    """Read a specified CSV file into a Dataframe.

    Args:
        file_path: Path to CSV file.
        delim: CSV separator.
        header_rows: Number of header rows.
        footer_rows: Number of footer rows.
        encod: CSV file encoding.

    Returns:
        pd.DataFrame: Dataframe read from CSV file.
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
        engine="python",
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL,
    )

    return df


def parse_data(
    *,
    df: pd.DataFrame,
    input_columns: list[str],
    output_columns: list[str],
    api_columns: list[str],
    cd_flags: list[str],
    date_format: str,
    date_dedupe: bool,
    fill_memo: bool,
    currency_fix: float,
    payee_mappings: dict[str, str],
    clean_payee: bool = True,
    clean_memo: bool = True,
) -> pd.DataFrame:
    """Convert each column of the dataframe to match ideal output data.

    Args:
        df: Dataframe to process.
        input_columns: Columns present in input data.
        output_columns: Desired columns to be present in output data.
        api_columns: Desired columns to be present in API data.
        cd_flags: Parameter to indicate inflow/outflow for a row.
        date_format: String format for date.
        date_dedupe: Whether to fill in date with previous if blank.
        fill_memo: Whether to fill blank memo with payee data.
        currency_fix: Value to divide all currency amounts by.
        payee_mappings: Dict of raw payee substring → friendly name.
        clean_payee: Whether to apply string cleaning to Payee field.
        clean_memo: Whether to apply string cleaning to Memo field.

    Returns:
        pd.DataFrame: Modified dataframe matching provided configuration values.
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
    # apply payee rename mappings
    df = apply_payee_mappings(df, payee_mappings)
    # fix strings
    if clean_payee:
        df["Payee"] = clean_strings(df["Payee"])
    if clean_memo:
        df["Memo"] = clean_strings(df["Memo"])
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


def apply_payee_mappings(
    df: pd.DataFrame, payee_mappings: dict[str, str]
) -> pd.DataFrame:
    """Replace raw payee strings with friendly names from a mapping dict.

    Matching is case-insensitive substring; first match wins.

    Args:
        df: Dataframe to modify.
        payee_mappings: Dict of raw substring → friendly name.

    Returns:
        pd.DataFrame: Modified dataframe.
    """
    if not payee_mappings:
        return df

    def map_payee(payee: str) -> str:
        if pd.isna(payee):
            return payee
        for raw, friendly in payee_mappings.items():
            if raw.lower() in str(payee).lower():
                return friendly
        return payee

    df["Payee"] = df["Payee"].apply(map_payee)
    return df


def merge_duplicate_columns(
    df: pd.DataFrame, input_columns: list[str]
) -> pd.DataFrame:
    """Merge columns specified more than once in the input_columns list.

    Converts values into strings before merging.

    Args:
        df: Dataframe to modify.
        input_columns: The list of columns in the input file.

    Returns:
        pd.DataFrame: Modified dataframe.
    """

    # create dictionary mapping column names to indices of duplicates
    cols_to_merge: dict[str, list[int]] = dict()
    for index, col in enumerate(input_columns):
        if col not in cols_to_merge:
            cols_to_merge[col] = []
        cols_to_merge[col] += [index]

    # go through each key
    for key in cols_to_merge:
        key_cols: list[int] = cols_to_merge[key]
        if len(key_cols) > 1:
            if key in {"Inflow", "Outflow"}:
                # merge numerically using fillna to preserve float dtype
                for dupe_count, key_col in enumerate(key_cols[1:]):
                    df.iloc[:, key_cols[0]] = df.iloc[:, key_cols[0]].fillna(
                        df.iloc[:, key_col]
                    )
                    df.columns.values[key_col] = f"{key} {dupe_count}"
            else:
                # build the merged values separately, then replace the column in one
                # step so pandas does not try to coerce strings back into float dtype.
                merged_col = df.iloc[:, key_cols[0]].fillna("").astype(str)
                # merge every duplicate column into the 1st instance
                # of the column name
                for dupe_count, key_col in enumerate(key_cols[1:]):
                    merged_col = (
                        merged_col
                        + " "
                        + df.iloc[:, key_col].fillna("").astype(str)
                    )
                    df.columns.values[key_col] = f"{key} {dupe_count}"
                df.isetitem(
                    key_cols[0],
                    merged_col.str.replace(
                        "\\s{2,}", " ", regex=True
                    ).str.strip().to_numpy(),
                )

    logging.debug(f"\nAfter duplicate merge\n{df.head()}")
    return df


def add_missing_columns(
    df: pd.DataFrame, input_cols: list[str], output_cols: list[str]
) -> pd.DataFrame:
    """Add any missing required columns to the Dataframe.

    Args:
        df: Dataframe to modify.
        input_cols: The list of columns in the input file.
        output_cols: The desired list of columns as output.

    Returns:
        pd.DataFrame: Modified dataframe.
    """
    # compare input & output column lists to find missing columns
    missing_cols = list(set(output_cols).difference(input_cols))
    # add missing output columns
    for col in missing_cols:
        df.insert(loc=0, column=col, value="")
        df[col] = pd.to_numeric(df[col], errors="coerce")
    logging.debug(f"\nAfter adding missing columns:\n{df.head()}")
    return df


def cd_flag_process(df: pd.DataFrame, cd_flags: list[str]) -> pd.DataFrame:
    """Fix columns where inflow/outflow is indicated by a flag in a separate column.

    The cd_flag list is in the form ["indicator column, outflow flag, inflow flag"].
    Uses the "CDFlag" column specified in Input Columns rather than the indicator
    flag in the flag list.

    Args:
        df: Dataframe to modify.
        cd_flags: List of parameters for applying indicators.

    Returns:
        pd.DataFrame: Modified dataframe.
    """
    if len(cd_flags) == 3:
        outflow_flag = cd_flags[2]
        # if this row is indicated to be outflow, make inflow negative
        df.loc[df["CDFlag"] == outflow_flag, ["Inflow"]] = -1 * df["Inflow"]
    return df


def fix_amount(df: pd.DataFrame, currency_fix: float) -> pd.DataFrame:
    """Fix currency string formatting and convert negative inflows/outflows.

    Args:
        df: Dataframe to modify.
        currency_fix: Value to divide all currency amounts by.

    Returns:
        pd.DataFrame: Modified dataframe.
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
    df["amount"] = (1000 * (df["Inflow"] - df["Outflow"])).astype(int)
    return df


def clean_monetary_values(num_series: pd.Series) -> pd.Series:
    """Clean a series of monetary strings into numeric values.

    Converts "," to ".", removes all but the last ".", strips non-numeric
    characters, and fills nulls with 0.

    Args:
        num_series: Series of values to modify.

    Returns:
        pd.Series: Modified series as floats.
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
    return_series: pd.Series[float] = num_series.fillna(value=0).astype(float)
    return return_series


def remove_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove invalid rows from dataframe.

    An invalid row is one without a date or without an Inflow or Outflow value.

    Args:
        df: Dataframe to modify.

    Returns:
        pd.DataFrame: Modified dataframe.
    """
    # filter out rows where Inflow and Outflow are both blank
    df.query("Inflow.notna() | Outflow.notna()", inplace=True)
    # filter rows with an invalid date
    df.query("Date.notna()", inplace=True)
    df[["Inflow", "Outflow", "amount"]] = df[
        ["Inflow", "Outflow", "amount"]
    ].fillna(0)
    df = df.loc[df["amount"].fillna(0) != 0].copy()
    df.reset_index(inplace=True)
    return df


def auto_memo(df: pd.DataFrame, fill_memo: bool) -> pd.DataFrame:
    """If memo is blank, fill with contents of payee column.

    Args:
        df: Dataframe to modify.
        fill_memo: Whether to fill blank memo with payee data.

    Returns:
        pd.DataFrame: Modified dataframe.
    """
    if fill_memo:
        df["Memo"] = df["Memo"].fillna(df["Payee"])
    return df


def auto_payee(df: pd.DataFrame) -> pd.DataFrame:
    """If Payee is blank, fill with contents of Memo column.

    Args:
        df: Dataframe to modify.

    Returns:
        pd.DataFrame: Modified dataframe.
    """
    df["Payee"] = df["Payee"].fillna(df["Memo"])
    return df


def clean_strings(string_series: pd.Series) -> pd.Series:
    """Perform various cleaning operations on provided string series.

    Args:
        string_series: String series to modify.

    Returns:
        pd.Series: Cleaned series.
    """
    modified_string_series = string_series
    # convert string to title case
    modified_string_series = modified_string_series.str.title()
    # remove non-alphanumeric
    modified_string_series = modified_string_series.replace(
        r"[^\w\d ]", " ", regex=True
    )
    # remove newline characters
    modified_string_series = modified_string_series.str.replace(
        "\n", " ", regex=True
    )
    # strip leading and trailing whitespace
    modified_string_series = modified_string_series.str.strip()
    # replace multiple spacing with single
    modified_string_series = modified_string_series.str.replace(
        " +", " ", regex=True
    )
    return modified_string_series


def fix_date(date_series: pd.Series, date_format: str) -> pd.Series:
    """Process dates from input format to ISO format.

    Any non-parseable dates are returned as a NaT null value.

    Args:
        date_series: Series of dates to process.
        date_format: Date format codes per the 1989 C standard.

    Returns:
        pd.Series: Series with dates in ISO format.
    """
    formatted_date_series = pd.to_datetime(
        date_series,
        format=date_format,
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")

    logging.debug(f"\nFixed dates:\n{date_series.head()}")

    return formatted_date_series


def fill_empty_dates(date_series: pd.Series, fill_dates: bool) -> pd.Series:
    """Fill in empty dates with values from previous cells.

    Args:
        date_series: Data series to modify.
        fill_dates: Whether to fill in empty dates or not.

    Returns:
        pd.Series: Modified data series.
    """
    if fill_dates:
        date_series = date_series.replace(r"^\s*$", pd.NA, regex=True)
        date_series = date_series.ffill()

    return date_series


def fill_api_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Generate API-specific columns using data in dataframe.

    Args:
        df: Dataframe to read & modify.

    Returns:
        pd.DataFrame: Dataframe with additional columns added.
    """
    df["account_id"] = ""
    df["date"] = df["Date"].astype(str)
    df["payee_name"] = df["Payee"].str.slice(0, 50)
    df["memo"] = df["Memo"].str.slice(0, 100)
    df["category"] = ""
    df["cleared"] = "cleared"
    df["payee_id"] = ""
    df["category_id"] = ""
    df["approved"] = False
    df["flag_color"] = ""

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


def combine_dfs(df_list: list[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate a list of provided dataframes.

    Args:
        df_list: List of dataframes to concatenate.

    Returns:
        pd.DataFrame: Concatenated dataframe.
    """
    merged_df = pd.concat(df_list, ignore_index=True).drop_duplicates()
    return merged_df
