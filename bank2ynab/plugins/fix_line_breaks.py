from ..bank_handler import BankHandler


class FixLineBreaksPlugin(BankHandler):
    def __init__(self, config_dict: dict):
        super().__init__(config_dict)
        self.name = "FixLineBreaks"

    def _preprocess_file(self, file_path: str, plugin_args: list) -> None:
        """Remove all linebreaks followed by any character specified in plugin_args.

        Args:
            file_path: Path of file to modify.
            plugin_args: Target characters after which linebreaks are removed.
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
