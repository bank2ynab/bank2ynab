from os.path import join, abspath, dirname

PRODPATH = "bank2ynab.conf"
TESTCONFPATH = join("test-data", "test.conf")

def get_test_confparser():
    py2 = False
    try:
        import configparser
        # probably could do with a few more imports just in case
    except ImportError:
        import ConfigParser as configparser
        py2 = True
    cp = configparser.ConfigParser()
    # first read prod to get all defaults
    cp.read([PRODPATH])
    for section in cp.sections():
        cp.remove_section(section)
    # then read any test-specific config
    cp.read([TESTCONFPATH])

    return cp, py2