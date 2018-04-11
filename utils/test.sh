#!/bin/bash

path_git=~/svn/gb.torben/code/git/bank2ynab
path_download=~/Downloads

# copy test files
cp $path_git/test-data/*.csv $path_download
cp $path_git/test-data/*.CSV $path_download

# run the script
python3 $path_git/bank2ynab.py

# show the results
ls $path_download/fixed*.*
