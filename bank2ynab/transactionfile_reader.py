import codecs
import logging
import os
import re
from os.path import abspath, join

import chardet


class TransactionFileReader:
    """
    find all relevant files for a specified config and provide a dataframe to work with
    """

    def __init__(
        self,
        *,
        name: str,
        file_pattern: str,
        try_path: str,
        regex_active: bool,
        ext: str,
        prefix: str,
    ) -> None:
        """
        generate bank specific file reader using supplied configuration flags


        """
        self.name = name
        self.file_pattern = file_pattern
        self.try_path = try_path
        self.regex_active = regex_active
        self.ext = ext
        self.prefix = prefix

        self.files = self.get_files()

    def get_files(self) -> list:
        """
        gets list of matching transaction files

        :return: list of files to process
        :rtype: list
        """

        files = list()
        missing_dir = False
        path = ""
        if self.file_pattern != "":
            try:
                path = self.find_directory(self.try_path)
            except FileNotFoundError:
                missing_dir = True
                path = self.find_directory("")
            path = abspath(path)
            try:
                directory_list = os.listdir(path)
            except FileNotFoundError:
                directory_list = os.listdir(".")
            if self.regex_active is True:
                files = [
                    join(path, f)
                    for f in directory_list
                    if f.endswith(self.ext)
                    if re.match(self.file_pattern + r".*\.", f)
                    if self.prefix not in f
                ]
            else:
                files = [
                    join(path, f)
                    for f in directory_list
                    if f.endswith(self.ext)
                    if f.startswith(self.file_pattern)
                    if self.prefix not in f
                ]
            if not files and missing_dir:
                logging.error(
                    f"\nFormat: {self.name}\n\nError: Can't find download path: {self.try_path}\nTrying default path instead:\t {path}"
                )
        return files

    def detect_encoding(self, filepath):
        """
        Utility to detect file encoding. This is imperfect, but
        should work for the most common cases.
        :param filepath: string path to a given file
        :return: encoding alias that can be used with open()
        """
        # First try to guess the encoding with chardet. Take it if the
        # confidence is >60% (randomly chosen)
        with open(filepath, "rb") as f:
            file_content = f.read()
            rslt = chardet.detect(file_content)
            confidence, encoding = rslt["confidence"], rslt["encoding"]
            if confidence > 0.6:
                logging.info(
                    "\tOpening file using encoding {} with confidence {}".format(
                        encoding, confidence
                    )
                )
                return encoding

        # because some encodings will happily encode anything even if wrong,
        # keeping the most common near the top should make it more likely that
        # we're doing the right thing.
        encodings = [
            "ascii",
            "utf-8",
            "utf-16",
            "cp1251",
            "utf_32",
            "utf_32_be",
            "utf_32_le",
            "utf_16",
            "utf_16_be",
            "utf_16_le",
            "utf_7",
            "utf_8_sig",
            "cp850",
            "cp852",
            "latin_1",
            "big5",
            "big5hkscs",
            "cp037",
            "cp424",
            "cp437",
            "cp500",
            "cp720",
            "cp737",
            "cp775",
            "cp855",
            "cp856",
            "cp857",
            "cp858",
            "cp860",
            "cp861",
            "cp862",
            "cp863",
            "cp864",
            "cp865",
            "cp866",
            "cp869",
            "cp874",
            "cp875",
            "cp932",
            "cp949",
            "cp950",
            "cp1006",
            "cp1026",
            "cp1140",
            "cp1250",
            "cp1252",
            "cp1253",
            "cp1254",
            "cp1255",
            "cp1256",
            "cp1257",
            "cp1258",
            "euc_jp",
            "euc_jis_2004",
            "euc_jisx0213",
            "euc_kr",
            "gb2312",
            "gbk",
            "gb18030",
            "hz",
            "iso2022_jp",
            "iso2022_jp_1",
            "iso2022_jp_2",
            "iso2022_jp_2004",
            "iso2022_jp_3",
            "iso2022_jp_ext",
            "iso2022_kr",
            "latin_1",
            "iso8859_2",
            "iso8859_3",
            "iso8859_4",
            "iso8859_5",
            "iso8859_6",
            "iso8859_7",
            "iso8859_8",
            "iso8859_9",
            "iso8859_10",
            "iso8859_11",
            "iso8859_13",
            "iso8859_14",
            "iso8859_15",
            "iso8859_16",
            "johab",
            "koi8_r",
            "koi8_u",
            "mac_cyrillic",
            "mac_greek",
            "mac_iceland",
            "mac_latin2",
            "mac_roman",
            "mac_turkish",
            "ptcp154",
            "shift_jis",
            "shift_jis_2004",
            "shift_jisx0213",
        ]
        result = None
        error = (
            ValueError,
            UnicodeError,
            UnicodeDecodeError,
            UnicodeEncodeError,
        )
        for enc in encodings:
            try:
                logging.info(
                    "\tAttempting to open file using {} encoding...".format(
                        enc
                    )
                )
                with codecs.open(filepath, "r", encoding=enc) as f:
                    for line in f:
                        line.encode("utf-8")
                    return enc
            except error:
                continue

        return result

    def find_directory(self, filepath):
        """finds the downloads folder for the active user if filepath is not set"""
        if filepath == "":
            if os.name == "nt":
                # Windows
                import winreg

                shell_path = (
                    "SOFTWARE\\Microsoft\\Windows\\CurrentVersion"
                    "\\Explorer\\Shell Folders"
                )
                dl_key = "{374DE290-123F-4565-9164-39C4925E467B}"
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, shell_path
                ) as key:
                    input_dir = winreg.QueryValueEx(key, dl_key)[0]
            else:
                # Linux, OSX
                userhome = os.path.expanduser("~")
                input_dir = os.path.join(userhome, "Downloads")
        else:
            if not os.path.exists(filepath):
                s = "Error: Input directory not found: {}"
                raise FileNotFoundError(s.format(filepath))
            input_dir = filepath
        return input_dir
