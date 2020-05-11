import sys
from os.path import join, realpath, dirname

project_dirname = dirname(dirname(realpath(__file__)))
sys.path.append(join(project_dirname, "bank2ynab"))
