import configparser
import logging
import os
import shutil
import typing
from importlib import resources
from pathlib import Path

from platformdirs import user_config_dir


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

    def fix_conf_params(self, section: str) -> dict[str, typing.Any]:
        """Return a dictionary of all parameters for a given config section.

        Uses ConfigParser defaults under [DEFAULT] if present.

        Args:
            section: Name of section in config file, e.g. "MyBank"
                matches "[MyBank]" in file.

        Returns:
            dict[str, Any]: Dictionary matching shorthand strings to config values.
        """

        bank_config = {
            "bank_name": section,
            "input_columns": self.get_config_line_lst(
                section, "Input Columns", ","
            ),
            "output_columns": self.get_config_line_lst(
                section, "Output Columns", ","
            ),
            "api_columns": self.get_config_line_lst(
                section, "API Transaction Fields", ","
            ),
            "input_filename": self.get_config_line_str(
                section, "Source Filename Pattern"
            ),
            "path": self.get_config_line_str(section, "Source Path"),
            "ext": self.get_config_line_str(
                section, "Source Filename Extension"
            ),
            "encoding": self.get_config_line_str(section, "Encoding"),
            "regex": self.get_config_line_boo(
                section, "Use Regex For Filename"
            ),
            "fixed_prefix": self.get_config_line_str(
                section, "Output Filename Prefix"
            ),
            "output_ext": self.get_config_line_str(
                section, "Output Filename Extension"
            ),
            "input_delimiter": self.get_config_line_str(
                section, "Source CSV Delimiter"
            ),
            "header_rows": self.get_config_line_int(section, "Header Rows"),
            "footer_rows": self.get_config_line_int(section, "Footer Rows"),
            "date_format": self.get_config_line_str(section, "Date Format"),
            "date_dedupe": self.get_config_line_boo(
                section, "Date De-Duplication"
            ),
            "delete_original": self.get_config_line_boo(
                section, "Delete Source File"
            ),
            "cd_flags": self.get_config_line_lst(
                section, "Inflow or Outflow Indicator", ","
            ),
            "payee_to_memo": self.get_config_line_boo(
                section, "Use Payee for Memo"
            ),
            "plugin": self.get_config_line_str(section, "Plugin"),
            "plugin_args": self.get_config_line_lst(
                section, "Plugin Arguments", "\n"
            ),
            "api_token": self.get_config_line_str(
                section, "YNAB API Access Token"
            ),
            "api_account": self.get_config_line_lst(
                section, "YNAB Account ID", "|"
            ),
            "currency_mult": self.get_config_line_flt(
                section, "Currency Conversion Factor"
            ),
            "save_output": self.get_config_line_boo(
                section, "Save Output File"
            ),
        }

        # quick n' dirty fix for tabs as delimiters
        if bank_config["input_delimiter"] == "\\t":
            bank_config["input_delimiter"] = "\t"

        return bank_config

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
