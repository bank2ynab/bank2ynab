from os.path import join

PRODPATH = "bank2ynab.conf"
TESTCONFPATH = join("test-data", "test.conf")


def get_test_confparser():
    import configparser

    cp = configparser.RawConfigParser()
    # first read prod to get all defaults
    cp.read([PRODPATH])
    for section in cp.sections():
        cp.remove_section(section)
    # then read any test-specific config
    cp.read([TESTCONFPATH])

    return cp
