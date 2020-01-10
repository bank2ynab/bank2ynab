# Plugin for handling format of Handelsbanken [SE] bank export files
"""
        Strip HTML from input file, allowing it to be used by main script
        With thanks to @joacand's script from here:
        github.com/joacand/HandelsbankenYNABConverter/blob/master/Converter.py
"""
from bank2ynab import B2YBank
import re


class Handelsbanken(B2YBank):
    def __init__(self, config_object):
        """
        :param config_object: a dictionary of conf parameters
        """
        super(Handelsbanken, self).__init__(config_object)
        self.name = "Handelsbanken"

    def _preprocess_file(self, file_path):
        """
        Strips HTML from input file, modifying the input file directly
        :param file_path: path to file
        """
        with open(file_path) as input_file:
            output_rows = []
            for row in input_file:
                cells = row.split(";")
                new_row = []
                for cell in cells:
                    es = re.findall(r"\>.*?\<", cell)
                    while "><" in es:
                        es.remove("><")
                        for n, i in enumerate(es):
                            es[n] = i[1:-1]
                    # if our cell isn't empty, add it to the row
                    if len(es) > 0:
                        new_row.append(es[0])
                # if our row isn't empty, add it to the list of rows
                if new_row:
                    output_rows.append(new_row)
        # overwrite our source file
        with open(file_path, "w") as output_file:
            for row in output_rows:
                output_file.write("{}\n".format(";".join(row)))
        return


def build_bank(config):
    """ This factory function is called from the main program,
    and expected to return a B2YBank subclass.
    Without this, the module will fail to load properly.

    :param config: dict containing all available configuration parameters
    :return: a B2YBank subclass instance
    """
    return Handelsbanken(config)
