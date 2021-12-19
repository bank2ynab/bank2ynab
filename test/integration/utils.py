from os.path import join, dirname, realpath

PRODPATH = "bank2ynab.conf"
TESTCONFPATH = join("test-data", "test.conf")


def get_test_confparser():
    import configparser

    cp = configparser.RawConfigParser()
    # convert our paths into absolutes

    project_dir = get_project_dir()
    prodpath = join(project_dir, PRODPATH)
    testconfpath = join(project_dir, TESTCONFPATH)

    # first read prod to get all defaults
    cp.read([prodpath])
    for section in cp.sections():
        cp.remove_section(section)
    # then read any test-specific config
    cp.read([testconfpath])

    return cp


def get_project_dir():
    path = realpath(__file__)
    return dirname(dirname(path))
