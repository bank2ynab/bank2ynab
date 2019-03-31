#!/bin/bash
# echo "The script you are running has basename `basename "$0"`, dirname `dirname "$0"`"
# echo "The present working directory is `pwd`"
#echo "Bash script for running bank2ynab.py"
#echo "The present working directory is `pwd`"
#echo "changing directory to: `dirname "$0"`"
cd `dirname "$0"`
#echo "going one directory up.."
cd ..
#echo "The present working directory is `pwd`"
#echo "========== bank2ynab ==========="
#python3 instead of python, due to error with python2 somehow
python3 bank2ynab.py
