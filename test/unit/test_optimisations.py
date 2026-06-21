"""Tests for the optimisation batch (issues #492–#497, PR #503).

Each section targets one of the six issues. The scenarios below map directly
to the PR test plan; additional edge-case coverage is included where useful.
"""

import importlib
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from bank2ynab.bank_handler import BankPlugin, build_bank
from bank2ynab.config_handler import BankConfig
from bank2ynab.dataframe_handler import (
    DataframeHandler,
    TransactionSource,
    _parse_monetary_string,
    clean_monetary_values,
    fix_amount,
)

# ── Shared helpers ─────────────────────────────────────────────────────────────


def _make_config(**overrides) -> BankConfig:
    """Return a BankConfig with all required fields set to safe defaults.

    Any kwarg overrides the corresponding field, so callers only need to
    supply what their test actually cares about.
    """
    defaults = dict(
        bank_name="Test Bank",
        # Five-column layout: Date / Payee / Memo / Outflow / Inflow
        input_columns=["Date", "Payee", "Memo", "Outflow", "Inflow"],
        output_columns=["Date", "Payee", "Memo", "Outflow", "Inflow"],
        # Subset of columns produced by fill_api_columns + fix_amount
        api_columns=[
            "date",
            "payee_name",
            "memo",
            "amount",
            "account_id",
            "import_id",
            "cleared",
            "approved",
            "flag_color",
            "payee_id",
            "category_id",
            "category",
        ],
        input_filename="",
        path="",
        ext=".csv",
        encoding="utf-8",
        regex=False,
        fixed_prefix="",
        output_ext=".csv",
        input_delimiter=",",
        header_rows=0,
        footer_rows=0,
        date_format="%Y-%m-%d",
        date_dedupe=False,
        delete_original=False,
        cd_flags=[],
        payee_to_memo=False,
        plugin="",
        plugin_args=[],
        api_token="",
        api_account=[],
        currency_mult=1.0,
        save_output=False,
        payee_mappings={},
        clean_payee=False,
        clean_memo=False,
    )
    defaults.update(overrides)
    return BankConfig(**defaults)


# ── #497: Monetary string parsing ─────────────────────────────────────────────


class TestParseMonetaryString:
    """_parse_monetary_string: PR test plan scenarios and edge cases.

    The two format scenarios from the PR test plan are:
      * European: "1.234,56" → 1234.56 (period as thousands, comma as decimal)
      * US:       "1,234.56" → 1234.56 (comma as thousands, period as decimal)
    """

    def test_european_format(self):
        """Period-thousands, comma-decimal → 1234.56."""
        assert _parse_monetary_string("1.234,56") == pytest.approx(1234.56)

    def test_us_format(self):
        """Comma-thousands, period-decimal → 1234.56."""
        assert _parse_monetary_string("1,234.56") == pytest.approx(1234.56)

    def test_plain_decimal(self):
        assert _parse_monetary_string("1234.56") == pytest.approx(1234.56)

    def test_negative_value(self):
        assert _parse_monetary_string("-42.50") == pytest.approx(-42.50)

    def test_integer_string(self):
        assert _parse_monetary_string("100") == pytest.approx(100.0)

    def test_null_returns_zero(self):
        assert _parse_monetary_string(None) == 0.0

    def test_nan_returns_zero(self):
        assert _parse_monetary_string(float("nan")) == 0.0

    def test_empty_string_returns_zero(self):
        assert _parse_monetary_string("") == 0.0

    def test_whitespace_only_returns_zero(self):
        assert _parse_monetary_string("   ") == 0.0

    def test_non_numeric_returns_zero(self):
        assert _parse_monetary_string("n/a") == 0.0

    def test_already_a_float(self):
        assert _parse_monetary_string(9.99) == pytest.approx(9.99)

    def test_zero(self):
        assert _parse_monetary_string("0.00") == 0.0

    def test_large_european_amount(self):
        """Multiple thousands-separator periods are all stripped."""
        assert _parse_monetary_string("1.234.567,89") == pytest.approx(1234567.89)


class TestCleanMonetaryValues:
    """clean_monetary_values: series-level wrapper over _parse_monetary_string."""

    def test_mixed_formats_in_series(self):
        series = pd.Series(["1.234,56", "1,234.56", None, "0.00"])
        result = clean_monetary_values(series)
        assert list(result) == pytest.approx([1234.56, 1234.56, 0.0, 0.0])

    def test_series_of_plain_floats(self):
        series = pd.Series([10.5, 20.0, 0.0])
        result = clean_monetary_values(series)
        assert list(result) == pytest.approx([10.5, 20.0, 0.0])


# ── #497: Milliunit rounding ───────────────────────────────────────────────────


class TestMilliunitRounding:
    """fix_amount: rounds before astype(int) to prevent float truncation.

    The classic hazard: 2.29 * 1000 == 2289.9999999999998 in IEEE-754 float.
    Without .round(), astype(int) truncates to 2289 rather than the correct 2290.
    PR test plan: "amounts like €9.999 produce 9999 milliunits rather than 9998."
    """

    def _df(self, inflow: float, outflow: float) -> pd.DataFrame:
        return pd.DataFrame({"Inflow": [inflow], "Outflow": [outflow]})

    def test_float_truncation_hazard(self):
        """2.29 * 1000 = 2289.999... — must round to 2290, not truncate to 2289."""
        df = fix_amount(self._df(2.29, 0.0), currency_fix=1.0)
        assert df["amount"].iloc[0] == 2290

    def test_pr_example_9_999(self):
        """PR test plan example: 9.999 → 9999 milliunits."""
        df = fix_amount(self._df(9.999, 0.0), currency_fix=1.0)
        assert df["amount"].iloc[0] == 9999

    def test_exact_integer_amount(self):
        """Clean €10.00 → 10000 milliunits with no rounding artefacts."""
        df = fix_amount(self._df(10.00, 0.0), currency_fix=1.0)
        assert df["amount"].iloc[0] == 10000

    def test_outflow_produces_negative_amount(self):
        df = fix_amount(self._df(0.0, 5.50), currency_fix=1.0)
        assert df["amount"].iloc[0] == -5500

    def test_currency_mult_divides_before_milliunit_conversion(self):
        """currency_mult=100 divides by 100, then converts to milliunits."""
        # 10000 / 100 = 100.00 → 100_000 milliunits
        df = fix_amount(self._df(10000.0, 0.0), currency_fix=100.0)
        assert df["amount"].iloc[0] == 100000

    def test_negative_inflow_becomes_outflow(self):
        """A negative inflow is flipped to an outflow before milliunit calc."""
        df = fix_amount(self._df(-20.0, 0.0), currency_fix=1.0)
        assert df["amount"].iloc[0] == -20000


# ── #496: BankPlugin Protocol compliance ──────────────────────────────────────


class TestBankPluginProtocol:
    """All shipping plugins must satisfy the BankPlugin Protocol at load time.

    The PR test plan: "All existing plugin files (handelsbanken, parse_from_memo,
    null, etc.) satisfy BankPlugin — verify with isinstance(bank, BankPlugin)."

    Note: fix_line_breaks._preprocess_file is missing its return statement and
    returns None implicitly — a pre-existing bug. The isinstance check passes
    because runtime_checkable only validates method presence, not signatures.
    That bug is tracked separately.
    """

    @pytest.fixture
    def config(self):
        return _make_config()

    def _load(self, plugin_name: str, config: BankConfig) -> object:
        module = importlib.import_module(f".plugins.{plugin_name}", package="bank2ynab")
        return module.build_bank(config)

    def test_null_plugin(self, config):
        assert isinstance(self._load("null", config), BankPlugin)

    def test_handelsbanken_plugin(self, config):
        assert isinstance(self._load("handelsbanken", config), BankPlugin)

    def test_fix_line_breaks_plugin(self, config):
        assert isinstance(self._load("fix_line_breaks", config), BankPlugin)

    def test_ocbc_bank_sg_plugin(self, config):
        assert isinstance(self._load("OCBC_Bank_SG", config), BankPlugin)

    def test_pdf_converter_plugin(self, config):
        assert isinstance(self._load("pdf_converter", config), BankPlugin)

    def test_xls_converter_plugin(self, config):
        assert isinstance(self._load("xls_converter", config), BankPlugin)

    def test_parse_from_memo_plugin(self):
        """parse_from_memo requires at least one regex in plugin_args."""
        config = _make_config(plugin_args=[r"(?P<payee>\w+)\s+(?P<memo>.*)"])
        assert isinstance(self._load("parse_from_memo", config), BankPlugin)

    def test_build_bank_raises_for_non_compliant_plugin(self):
        """build_bank() raises ImportError when a plugin returns an object
        without _preprocess_file, i.e. fails the BankPlugin Protocol check."""
        fake_bank = MagicMock(spec=[])  # no attributes at all
        fake_module = MagicMock()
        fake_module.build_bank.return_value = fake_bank

        config = _make_config(plugin="null")
        with patch(
            "bank2ynab.bank_handler.importlib.import_module",
            return_value=fake_module,
        ):
            with pytest.raises(ImportError, match="BankPlugin protocol"):
                build_bank(config)


# ── #492: TransactionSource Protocol ──────────────────────────────────────────


class TestTransactionSourceProtocol:
    """TransactionSource is structural: any class with read() -> DataFrame
    qualifies, without inheriting from anything."""

    def test_arbitrary_class_satisfies_protocol(self):
        """A plain in-memory class satisfies TransactionSource at runtime."""

        class InMemorySource:
            def __init__(self, df: pd.DataFrame) -> None:
                self._df = df

            def read(self) -> pd.DataFrame:
                return self._df

        assert isinstance(InMemorySource(pd.DataFrame()), TransactionSource)

    def test_class_without_read_does_not_satisfy_protocol(self):
        """An object without read() is not a TransactionSource."""

        class NoRead:
            pass

        assert not isinstance(NoRead(), TransactionSource)

    def test_dataframe_handler_accepts_in_memory_source(self):
        """DataframeHandler.run() works end-to-end with an in-memory source,
        so test code never needs to create a file on disk.

        The raw DataFrame mirrors what read_csv() produces: integer column
        names, no header row — parse_data() renames columns from input_columns.
        """
        raw = pd.DataFrame(
            {
                0: ["2024-01-15"],  # Date
                1: ["Corner Shop"],  # Payee
                2: ["groceries"],  # Memo
                3: ["0.00"],  # Outflow
                4: ["25.00"],  # Inflow
            }
        )

        class InMemorySource:
            def read(self) -> pd.DataFrame:
                return raw.copy()

        config = _make_config()
        handler = DataframeHandler()
        handler.run(source=InMemorySource(), config=config)

        assert not handler.empty
        assert handler.df["Date"].iloc[0] == "2024-01-15"
        assert handler.df["Payee"].iloc[0] == "Corner Shop"
        # €25.00 inflow → 25 000 milliunits
        assert handler.df["amount"].iloc[0] == 25000

    def test_in_memory_source_with_european_amount(self):
        """Decimal parsing via _parse_monetary_string handles European-format
        amounts correctly even in a full DataframeHandler pipeline."""
        raw = pd.DataFrame(
            {
                0: ["2024-03-01"],
                1: ["Supermarkt"],
                2: ["Einkauf"],
                3: ["0,00"],  # European-format zero
                4: ["1.234,56"],  # European-format €1 234.56
            }
        )

        class InMemorySource:
            def read(self) -> pd.DataFrame:
                return raw.copy()

        handler = DataframeHandler()
        handler.run(source=InMemorySource(), config=_make_config())

        assert handler.df["amount"].iloc[0] == 1234560  # 1234.56 * 1000
