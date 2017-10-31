from os.path import join, abspath, dirname

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
    cp.read([TESTCONFPATH])
    return cp, py2