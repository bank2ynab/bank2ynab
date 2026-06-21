import csv
import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Protocol, runtime_checkable

import pandas as pd

from .config_handler import BankConfig


@runtime_checkable
class TransactionSource(Protocol):
    """Protocol for objects that supply a raw DataFrame of transaction rows.

    Decouples ``DataframeHandler`` from the filesystem: any object with a
    ``read()`` method returning a ``DataFrame`` satisfies this contract,
    making it straightforward to substitute in-memory sources for tests.
    """

    def read(self) -> pd.DataFrame: ...


class CSVTransactionSource:
    """Reads transaction data from a delimited text file.

    This is the production implementation of :class:`TransactionSource`; it
    wraps :func:`read_csv` and holds the parameters that are only known at
    runtime (file path and detected encoding).

    Args:
        file_path: Path to the CSV file.
        delim: Field delimiter character.
        header_rows: Number of header rows to skip.
        footer_rows: Number of footer rows to skip.
        encod: File encoding (as detected by the caller).
    """

    def __init__(
        self,
        file_path: str,
        delim: str,
        header_rows: int,
        footer_rows: int,
        encod: str,
    ) -> None:
        self.file_path = file_path
        self.delim = delim
        self.header_rows = header_rows
        self.footer_rows = footer_rows
        self.encod = encod

    def read(self) -> pd.DataFrame:
        """Read and return the raw CSV as a DataFrame.

        Returns:
            pd.DataFrame: Unprocessed rows from the source file.
        """
        return read_csv(
            file_path=self.file_path,
            delim=self.delim,
            header_rows=self.header_rows,
            footer_rows=self.footer_rows,
            encod=self.encod,
        )


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
        source: TransactionSource,
        config: BankConfig,
    ) -> None:
        """Complete handling of Dataframe creation & output.

        Args:
            source: A :class:`TransactionSource` that supplies the raw rows.
                Use :class:`CSVTransactionSource` for production file reads;
                inject an in-memory source for tests.
            config: Bank configuration supplying all transformation parameters.
        """
        # read data from source into dataframe
        self.df = source.read()
        # modify dataframe to match desired output
        self.df = parse_data(df=self.df, config=config)
        # check if dataframe is empty
        self.empty = self.df.empty
        # set final columns & order for output file
        self.output_df = self.df[config.output_columns]
        # set final columns & order for api output
        self.api_transaction_df = self.df[config.api_columns]


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


def parse_data(*, df: pd.DataFrame, config: BankConfig) -> pd.DataFrame:
    """Convert each column of the dataframe to match ideal output data.

    Each transformation step is a standalone function composed explicitly here.
    Accepting a single ``BankConfig`` rather than a dozen positional parameters
    makes the composition point readable and allows individual steps to be
    tested in isolation without instantiating a handler.

    Args:
        df: Dataframe to process.
        config: Bank configuration supplying all transformation parameters.

    Returns:
        pd.DataFrame: Modified dataframe matching provided configuration values.
    """
    # set column names based on input column list
    df.columns = config.input_columns
    # debug to see what our df is like before transformation
    logging.debug(f"\nInitial DF\n{df.head()}")
    # merge duplicate input columns
    merge_duplicate_columns(df, config.input_columns)
    # add missing columns
    add_missing_columns(df, config.input_columns, config.output_columns + config.api_columns)
    # fix date format — keep as datetime while filling, then format to ISO string
    df["Date"] = fix_date(df["Date"], config.date_format)
    df["Date"] = fill_empty_dates(df["Date"], config.date_dedupe)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    # fix inflow/outflow string formatting
    df["Inflow"] = clean_monetary_values(df["Inflow"])
    df["Outflow"] = clean_monetary_values(df["Outflow"])
    # process Inflow/Outflow flags
    df = cd_flag_process(df, config.cd_flags)
    # fix amounts (convert negative inflows and outflows etc)
    df = fix_amount(df, config.currency_mult)
    # auto fill memo from payee if required
    df = auto_memo(df, config.payee_to_memo)
    # auto fill payee from memo
    df = auto_payee(df)
    # apply payee rename mappings
    df = apply_payee_mappings(df, config.payee_mappings)
    # fix strings
    if config.clean_payee:
        df["Payee"] = clean_strings(df["Payee"])
    if config.clean_memo:
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


def apply_payee_mappings(df: pd.DataFrame, payee_mappings: dict[str, str]) -> pd.DataFrame:
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


def merge_duplicate_columns(df: pd.DataFrame, input_columns: list[str]) -> pd.DataFrame:
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
                    df.iloc[:, key_cols[0]] = df.iloc[:, key_cols[0]].fillna(df.iloc[:, key_col])
                    df.columns.values[key_col] = f"{key} {dupe_count}"
            else:
                # build the merged values separately, then replace the column in one
                # step so pandas does not try to coerce strings back into float dtype.
                merged_col = df.iloc[:, key_cols[0]].fillna("").astype(str)
                # merge every duplicate column into the 1st instance
                # of the column name
                for dupe_count, key_col in enumerate(key_cols[1:]):
                    merged_col = merged_col + " " + df.iloc[:, key_col].fillna("").astype(str)
                    df.columns.values[key_col] = f"{key} {dupe_count}"
                df.isetitem(
                    key_cols[0],
                    merged_col.str.replace("\\s{2,}", " ", regex=True).str.strip().to_numpy(),
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

    # create amount column for API (in milliunits); round before truncation
    # to avoid float representation errors (e.g. 9.999999 → 9 instead of 10)
    df["amount"] = (df["Inflow"] - df["Outflow"]).multiply(1000).round().astype(int)
    return df


def _parse_monetary_string(value: object) -> float:
    """Parse a single monetary string to a float via Decimal for precision.

    Using ``Decimal`` for the string-to-number conversion boundary avoids
    the silent corruption that arises when locale-formatted strings are fed
    directly to ``float()`` (e.g. ``float("1.234,56")`` raises rather than
    returning ``1234.56``).  The result is stored as a plain float because
    pandas requires a uniform numeric dtype for vectorised arithmetic.

    Args:
        value: Raw cell value — may be a string, int, float, or NaN.

    Returns:
        float: Parsed numeric value, or ``0.0`` if the input is null or
            cannot be interpreted as a number.
    """
    if pd.isna(value):
        return 0.0
    s = str(value).strip()
    if not s:
        return 0.0
    # normalise thousands/decimal separators: convert commas to periods, then
    # remove all but the last period so "1.234.567,89" → "1234567.89"
    s = s.replace(",", ".")
    parts = s.split(".")
    if len(parts) > 2:
        s = "".join(parts[:-1]) + "." + parts[-1]
    # strip everything except digits, a leading minus, and the decimal point
    s = re.sub(r"[^\d.\-]", "", s)
    if not s or s in ("-", "."):
        return 0.0
    try:
        return float(Decimal(s))
    except InvalidOperation:
        return 0.0


def clean_monetary_values(num_series: pd.Series) -> pd.Series:
    """Clean a series of monetary strings into numeric float values.

    Delegates per-cell parsing to :func:`_parse_monetary_string`, which uses
    ``Decimal`` at the string-to-number boundary to prevent silent corruption
    from locale-specific separators or floating-point parse artefacts.

    Args:
        num_series: Series of raw monetary values (strings, ints, floats, NaN).

    Returns:
        pd.Series: Series of ``float64`` values; unparseable entries become
            ``0.0``.
    """
    return num_series.apply(_parse_monetary_string)


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
    df[["Inflow", "Outflow", "amount"]] = df[["Inflow", "Outflow", "amount"]].fillna(0)
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
    modified_string_series = modified_string_series.replace(r"[^\w\d ]", " ", regex=True)
    # remove newline characters
    modified_string_series = modified_string_series.str.replace("\n", " ", regex=True)
    # strip leading and trailing whitespace
    modified_string_series = modified_string_series.str.strip()
    # replace multiple spacing with single
    modified_string_series = modified_string_series.str.replace(" +", " ", regex=True)
    return modified_string_series


def fix_date(date_series: pd.Series, date_format: str) -> pd.Series:
    """Parse dates to datetime, accepting values with or without a time component.

    Tries the configured format first. Rows that fail (NaT) are retried with
    the same format plus a " %H:%M:%S" suffix, so a mixed column — some cells
    date-only, others date+time — is handled transparently.

    Any values that still cannot be parsed are returned as NaT.

    Args:
        date_series: Series of dates to process.
        date_format: Date format codes per the 1989 C standard.

    Returns:
        pd.Series: Series of datetime64 values (NaT for unparseable entries).
    """
    result = pd.to_datetime(date_series, format=date_format, errors="coerce")

    # Only retry with a time suffix when the configured format is date-only;
    # formats that already include time codes would produce duplicate regex groups.
    _time_codes = {"%H", "%I", "%M", "%S", "%p", "%f"}
    format_has_time = any(code in date_format for code in _time_codes)

    if not format_has_time:
        failed = result.isna() & date_series.notna() & (date_series.astype(str).str.strip() != "")
        if failed.any():
            retry = pd.to_datetime(
                date_series[failed],
                format=date_format + " %H:%M:%S",
                errors="coerce",
            )
            result = result.copy()
            result[failed] = retry

    logging.debug(f"\nFixed dates:\n{result.head()}")

    return result


def fill_empty_dates(date_series: pd.Series, fill_dates: bool) -> pd.Series:
    """Fill in empty dates with values from previous cells.

    Expects a datetime64 series; NaT values are propagated forward when
    fill_dates is True.

    Args:
        date_series: Data series to modify.
        fill_dates: Whether to fill in empty dates or not.

    Returns:
        pd.Series: Modified data series.
    """
    if fill_dates:
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
    df["import_id"] = df.agg(lambda x: f"YNAB:{x['amount']}:{x['date']}:", axis=1)
    # count every instance of import id & add a counter to id
    df["same_id_count"] = (df.groupby(["import_id"]).cumcount() + 1).astype(str)
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
