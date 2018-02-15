# Plugin for handling format of Handelsbanken [SE] bank export files
"""
In progress...
"""
from bank2ynab import B2YBank
import re

class Handelsbanken(B2YBank):
    def __init__(self, config_object, is_py2):
        """
        :param config_object: a dictionary of conf parameters
        :param is_py2: boolean indicating if we're running under
                        Python 2.x
        """
        super(Handelsbanken, self).__init__(config_object, is_py2)
        self.name = "Handelsbanken"

    def _preprocess_file(self, file_path):
        """
        Strips html formatting from input file
        I THINK THAT IS ALL WE NEED TO DO BEFORE THE FILE IS READY. LET US SEE...
        :param file_path: path to file
        """
        print("Handelsbanken plugin triggered") # debug
        with open(file_path) as input_file:
            for row in input_file:
                # pretty sure that using a regex is the best way to do this
                # using code cannibalised from https://github.com/joacand/HandelsbankenYNABConverter/blob/master/Converter.py as a starting point - will credit if I actually use it!
                cells = row.split(";")
                new_cells = []
                for cell in cells:
                    es = re.findall('\>.*?\<', cell) 
                    while ("><" in es):
                        es.remove("><")
                        for n,i in enumerate(es):
                            es[n] = i[1:-1]
                    if len(es) > 0:
                        new_cells.append(es[0])
                    
                if new_cells:
                    print("{}\n".format(new_cells))
        return


def build_bank(config, is_py2):
    """ This factory function is called from the main program,
    and expected to return a B2YBank subclass.
    Without this, the module will fail to load properly.

    :param config: dict containing all available configuration parameters
    :param is_py2: boolean indicating whether we are running under Python 2.x
    :return: a B2YBank subclass instance
    """
    return Handelsbanken(config, is_py2)
