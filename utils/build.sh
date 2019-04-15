#!/bin/bash

# easier on the eyes:
clear
# reuse this function:
get_input ()
{ if [ -z "$2" ] # Is parameter #2 zero length?
  then
    echo "I didn't get 2 parameters. Exiting." ; exit
  else
    while true; do
      read -p "$1 Press 'Y' to continue, or any other key to skip: " -n 1 response
      case $response in
        [Yy]* )
          $2
          result=$?
          if [ $result -eq ""0"" ]; then
            echo "--OK--"
            break
          else
            echo "An error occurred: " $result ". Exiting!"
            exit
          fi
          ;; # yes I know that 'break' is never going to run, but it feels proper to have it there.
        *     ) echo "";echo "Nothing done."; break;;
      esac
    done
  fi
}
# remove old build files:
if [ -f ""dist/*"" ]
    then
      echo "rm..."
      rm dist/*
fi
# do the actual work:
get_input "Are you ready to BUILD the package?" "python setup.py bdist_wheel"
get_input "Are you ready to UPLOAD the package?" "twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
echo ""
exit
