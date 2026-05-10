import configparser
import logging
import os
import shutil
import typing
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

from platformdirs import user_config_dir


@dataclass
class BankConfig:
    bank_name: str
    input_columns: list[str]
    output_columns: list[str]
    api_columns: list[str]
    input_filename: str
    path: str
    ext: str
    encoding: str
    regex: bool
    fixed_prefix: str
    output_ext: str
    input_delimiter: str
    header_rows: int
    footer_rows: int
    date_format: str
    date_dedupe: bool
    delete_original: bool
    cd_flags: list[str]
    payee_to_memo: bool
    plugin: str
    plugin_args: list[str]
    api_token: str
    api_account: list[str]
    currency_mult: float
    save_output: bool
    payee_mappings: dict[str, str] = field(default_factory=dict)
    clean_payee: bool = True
    clean_memo: bool = True

    def __post_init__(self) -> None:
        if self.input_delimiter == "\\t":
            self.input_delimiter = "\t"


class ConfigHandler:
    def __init__(self, *, user_mode: bool = False) -> None:
        self.user_mode = user_mode

        self.config_dir = self._resolve_config_dir()
        self.bank_conf_path = str(self._resolve_bank_conf_path())
        self.user_conf_path = str(self._resolve_user_conf_path())

        self.config = self.get_configs()

    def _resolve_config_dir(self) -> Path:
        env_path = os.getenv("BANK2YNAB_CONFIG_DIR")
        if env_path:
            return Path(env_path)
        return Path(user_config_dir("bank2ynab", "bank2ynab"))

    def _ensure_config_dir_exists(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _copy_default_if_missing(
        self, target_path: Path, packaged_file_name: str
    ) -> None:
        if target_path.exists():
            return
        self._ensure_config_dir_exists()
        packaged_path = resources.files("bank2ynab.data").joinpath(
            packaged_file_name
        )
        with resources.as_file(packaged_path) as source_path:
            shutil.copyfile(str(source_path), str(target_path))

    def _resolve_bank_conf_path(self) -> Path:
        target_path = self.config_dir / "bank2ynab.conf"
        self._copy_default_if_missing(target_path, "bank2ynab.conf")
        return target_path

    def _resolve_user_conf_path(self) -> Path:
        target_path = self.config_dir / "user_configuration.conf"
        self._copy_default_if_missing(
            target_path, "user_configuration.conf.template"
        )
        return target_path

    def get_configs(self) -> configparser.RawConfigParser:
        """Retrieve all configuration parameters."""

        conf_files: list[str] = []

        if not self.user_mode:
            conf_files.append(self.bank_conf_path)
        conf_files.append(self.user_conf_path)
        try:
            if not os.path.exists(conf_files[0]):
                raise FileNotFoundError
        except FileNotFoundError:
            s = f"Configuration file not found: {conf_files[0]}"
            logging.error(s)
            raise FileNotFoundError(s)
        else:
            config = configparser.RawConfigParser()
            config.read(conf_files, encoding="utf-8")
            return config

    def fix_conf_params(self, section: str) -> BankConfig:
        """Return a BankConfig for a given config section.

        Uses ConfigParser defaults under [DEFAULT] if present.

        Args:
            section: Name of section in config file, e.g. "MyBank"
                matches "[MyBank]" in file.

        Returns:
            BankConfig: Typed configuration for the given bank section.
        """
        return BankConfig(
            bank_name=section,
            input_columns=self.config.get(section, "Input Columns").split(","),
            output_columns=self.config.get(section, "Output Columns").split(","),
            api_columns=self.config.get(section, "API Transaction Fields").split(","),
            input_filename=self.config.get(section, "Source Filename Pattern"),
            path=self.config.get(section, "Source Path"),
            ext=self.config.get(section, "Source Filename Extension"),
            encoding=self.config.get(section, "Encoding"),
            regex=self.config.getboolean(section, "Use Regex For Filename"),
            fixed_prefix=self.config.get(section, "Output Filename Prefix"),
            output_ext=self.config.get(section, "Output Filename Extension"),
            input_delimiter=self.config.get(section, "Source CSV Delimiter"),
            header_rows=self.config.getint(section, "Header Rows"),
            footer_rows=self.config.getint(section, "Footer Rows"),
            date_format=self.config.get(section, "Date Format"),
            date_dedupe=self.config.getboolean(section, "Date De-Duplication"),
            delete_original=self.config.getboolean(section, "Delete Source File"),
            cd_flags=self.config.get(section, "Inflow or Outflow Indicator").split(","),
            payee_to_memo=self.config.getboolean(section, "Use Payee for Memo"),
            plugin=self.config.get(section, "Plugin"),
            plugin_args=self.config.get(section, "Plugin Arguments").split("\n"),
            api_token=self.config.get(section, "YNAB API Access Token"),
            api_account=self.config.get(section, "YNAB Account ID").split("|"),
            currency_mult=self.config.getfloat(section, "Currency Conversion Factor"),
            save_output=self.config.getboolean(section, "Save Output File"),
            payee_mappings={
                k: v
                for k, v in self.config.items(f"{section} payee_mappings")
                if k not in self.config.defaults()
            }
            if self.config.has_section(f"{section} payee_mappings")
            else {},
            clean_payee=self.config.getboolean(section, "Clean Payee"),
            clean_memo=self.config.getboolean(section, "Clean Memo"),
        )

    def get_config_line_str(self, section_name: str, param: str) -> str:
        """Returns a string value from a given section in the config object.

        Args:
            section_name: Section to search for parameter.
            param: Parameter to obtain from section.

        Returns:
            str: Value matching parameter.
        """
        return self.config.get(section_name, param)

    def get_config_line_int(self, section_name: str, param: str) -> int:
        """Returns an integer value from a given section in the config object.

        Args:
            section_name: Section to search for parameter.
            param: Parameter to obtain from section.

        Returns:
            int: Value matching parameter.
        """
        return self.config.getint(section_name, param)

    def get_config_line_flt(self, section_name: str, param: str) -> float:
        """Returns a float value from a given section in the config object.

        Args:
            section_name: Section to search for parameter.
            param: Parameter to obtain from section.

        Returns:
            float: Value matching parameter.
        """
        return self.config.getfloat(section_name, param)

    def get_config_line_boo(self, section_name: str, param: str) -> bool:
        """Returns a bool value from a given section in the config object.

        Args:
            section_name: Section to search for parameter.
            param: Parameter to obtain from section.

        Returns:
            bool: Value matching parameter.
        """
        return self.config.getboolean(section_name, param)

    def get_config_line_lst(
        self, section_name: str, param: str, splitter: str
    ) -> list[typing.Any]:
        """Returns a list value from a given section in the config object.

        Args:
            section_name: Section to search for parameter.
            param: Parameter to obtain from section.
            splitter: String to split the config value by.

        Returns:
            list: Value matching parameter.
        """
        return self.config.get(section_name, param).split(splitter)

    def get_log_level(self) -> int:
        """Return the logging level integer from config, defaulting to WARNING.

        Reads 'Log Level' from [DEFAULT]. Accepted values: DEBUG, INFO,
        WARNING, ERROR, CRITICAL.
        """
        level_str = self.config.defaults().get("log level", "WARNING").upper()
        level = getattr(logging, level_str, None)
        if not isinstance(level, int):
            logging.warning(f"Invalid log level '{level_str}', using WARNING.")
            return logging.WARNING
        return level
