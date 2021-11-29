import logging


# Generic utilities
def option_selection(options, msg):
    """
    Used to select from a list of options
    If only one item in list, selects that by default
    Otherwise displays "msg" asking for input selection (integer only)
    :param options: list of [name, option] pairs to select from
    :param msg: the message to display on the input line
    :return option_selected: the selected item from the list
    """
    selection = 1
    count = len(options)
    if count > 1:
        index = 0
        for option in options:
            index += 1
            print("| {} | {}".format(index, option[0]))
        selection = int_input(1, count, msg)
    option_selected = options[selection - 1][1]
    return option_selected


def int_input(min, max, msg):
    """
    Makes a user select an integer between min & max stated values
    :param  min: the minimum acceptable integer value
    :param  max: the maximum acceptable integer value
    :param  msg: the message to display on the input line
    :return user_input: sanitised integer input in acceptable range
    """
    while True:
        try:
            user_input = int(
                input("{} (range {} - {}): ".format(msg, min, max))
            )
            if user_input not in range(min, max + 1):
                raise ValueError
            break
        except ValueError:
            logging.info(
                "This integer is not in the acceptable range, try again!"
            )
    return user_input


def string_num_diff(str1, str2):
    """
    converts strings to floats and subtracts 1 from 2
    also convert output to "milliunits"
    """
    try:
        num1 = float(str1)
    except ValueError:
        num1 = 0.0
    try:
        num2 = float(str2)
    except ValueError:
        num2 = 0.0

    difference = int(1000 * (num2 - num1))
    return difference
