from ..bank_handler import BankHandler


class FixLineBreaksPlugin(BankHandler):
    def __init__(self, config_dict: dict):
        super().__init__(config_dict)
        self.name = "FixLineBreaks"

    def _preprocess_file(self, file_path: str, plugin_args: list) -> str:
        """
        Remove all linebreaks followed by any character specified in
        plugin_args.

        :param file_path: path of file to modify
        :type file_path: str
        :param plugin_args: target characters
        :type plugin_args: list
        :return: file path
        :rtype: str
        """

        # Open the source file for reading
        with open(file_path, "r") as f:
            # Read the contents of the file
            file_contents = f.read()

        # Process the file contents to remove linebreaks
        modified_contents = file_contents

        for char in plugin_args:
            modified_contents = modified_contents.replace(
                f"/n{char}", f"{char}"
            )

        # Open the source file for writing and overwrite its contents
        with open(file_path, "w") as f:
            f.write(modified_contents)


def build_bank(config):
    return FixLineBreaksPlugin(config)
