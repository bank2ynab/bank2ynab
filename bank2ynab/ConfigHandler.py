import configparser
import logging
import os


class ConfigHandler:
    def __init__(self) -> None:
        self.config = self.get_configs()

    def get_configs(self) -> configparser.RawConfigParser:
        """Retrieve all configuration parameters."""
        # TODO - fix path for these
        path = os.path.realpath(__file__)
        parent_dir = os.path.dirname(path)
        project_dir = os.path.dirname(parent_dir)
        conf_files = [
            os.path.join(project_dir, "bank2ynab.conf"),
            os.path.join(project_dir, "user_configuration.conf"),
        ]
        try:
            if not os.path.exists(conf_files[0]):
                raise FileNotFoundError
        except FileNotFoundError:
            s = "Configuration file not found: {}".format(conf_files[0])
            logging.error(s)
            raise FileNotFoundError(s)
        else:
            config = configparser.RawConfigParser()
            config.read(conf_files, encoding="utf-8")
            return config

    def fix_conf_params(self, section_name: str) -> dict:
        # TODO revise docstring
        # TODO revise argument passing? Make it clearer what the args do
        """from a ConfigParser object, return a dictionary of all parameters
        for a given section in the expected format.
        Because ConfigParser defaults to values under [DEFAULT] if present, these
        values should always appear unless the file is really bad.

        :param configparser_object: ConfigParser instance
        :param section_name: string of section name in config file
                            (e.g. "MyBank" matches "[MyBank]" in file)
        :return: dict with all parameters
        """
        config_mapping = {
            "input_columns": ["Input Columns", False, ","],
            "output_columns": ["Output Columns", False, ","],
            "input_filename": ["Source Filename Pattern", False, ""],
            "path": ["Source Path", False, ""],
            "ext": ["Source Filename Extension", False, ""],
            "encoding": ["Encoding", False, ""],
            "regex": ["Use Regex For Filename", True, ""],
            "fixed_prefix": ["Output Filename Prefix", False, ""],
            "input_delimiter": ["Source CSV Delimiter", False, ""],
            "header_rows": ["Header Rows", False, ""],
            "footer_rows": ["Footer Rows", False, ""],
            "date_format": ["Date Format", False, ""],
            "delete_original": ["Delete Source File", True, ""],
            "cd_flags": ["Inflow or Outflow Indicator", False, ","],
            "payee_to_memo": ["Use Payee for Memo", True, ""],
            "plugin": ["Plugin", False, ""],
            "api_token": ["YNAB API Access Token", False, ""],
            "api_account": ["YNAB Account ID", False, "|"],
        }

        bank_config = dict()
        for parameter in config_mapping:
            bank_config.update(
                {parameter: self.get_config_line(section_name, config_mapping[parameter])})

        bank_config.update({"bank_name": section_name})

        # quick n' dirty fix for tabs as delimiters
        if bank_config["input_delimiter"] == "\\t":
            bank_config["input_delimiter"] = "\t"

        return bank_config

    def get_config_line(self, section_name: str, args):
        """Get parameter for a given section in the expected format."""
        param = args[0]
        boolean = args[1]
        splitter = args[2]
        if boolean is True:
            line = self.config.getboolean(section_name, param)
        else:
            line = self.config.get(section_name, param)
            if splitter != "":
                line = line.split(splitter)
        return line
