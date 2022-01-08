import configparser
import logging
import os
import typing


class ConfigHandler:
    def __init__(self, *, user_mode: bool = False) -> None:
        self.user_mode = user_mode

        path = os.path.realpath(__file__)
        parent_dir = os.path.dirname(path)
        project_dir = os.path.dirname(parent_dir)

        self.bank_conf_path = os.path.join(project_dir, "bank2ynab.conf")
        self.user_conf_path = os.path.join(
            project_dir, "user_configuration.conf"
        )

        self.config = self.get_configs()

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
        """from a ConfigParser object, return a dictionary of all parameters
        for a given section in the expected format.
        Because ConfigParser defaults to values under [DEFAULT] if present,
        these values should always appear unless the file is really bad.

        :param section: name of section in config file to access
        (i.e. bank name, e.g. "MyBank" matches "[MyBank]" in file)
        :type section: str
        :return: dictionary matching shorthand strings to specified
        values in config
        :rtype: dict
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
        }

        # quick n' dirty fix for tabs as delimiters
        if bank_config["input_delimiter"] == "\\t":
            bank_config["input_delimiter"] = "\t"

        return bank_config

    def get_config_line_str(self, section_name: str, param: str) -> str:
        """
        Returns a string value from a given section in the config object.

        :param section_name: section to search for parameter
        :type section_name: str
        :param param: parameter to obtain from section
        :type param: str
        :return: value matching parameter
        :rtype: str
        """
        return self.config.get(section_name, param)

    def get_config_line_int(self, section_name: str, param: str) -> int:
        """
        Returns an integer value from a given section in the config object.

        :param section_name: section to search for parameter
        :type section_name: str
        :param param: parameter to obtain from section
        :type param: str
        :return: value matching parameter
        :rtype: int
        """
        return self.config.getint(section_name, param)

    def get_config_line_flt(self, section_name: str, param: str) -> float:
        """
        Returns a float value from a given section in the config object.

        :param section_name: section to search for parameter
        :type section_name: str
        :param param: parameter to obtain from section
        :type param: str
        :return: value matching parameter
        :rtype: float
        """
        return self.config.getfloat(section_name, param)

    def get_config_line_boo(self, section_name: str, param: str) -> bool:
        """
        Returns a bool value from a given section in the config object.

        :param section_name: section to search for parameter
        :type section_name: str
        :param param: parameter to obtain from section
        :type param: str
        :return: value matching parameter
        :rtype: bool
        """
        return self.config.getboolean(section_name, param)

    def get_config_line_lst(
        self, section_name: str, param: str, splitter: str
    ) -> list[typing.Any]:
        """
        Returns a list value from a given section in the config object.

        :param section_name: section to search for parameter
        :type section_name: str
        :param param: parameter to obtain from section
        :type param: str
        :return: value matching parameter
        :rtype: list
        """
        return self.config.get(section_name, param).split(splitter)
