def get_user_input(options: list, msg: str) -> str:
    """
    Used to select from a list of options.
    If only one item in list, selects that by default.
    Otherwise displays "msg" asking for input selection (integer only).

    :param options: list of [name, option] pairs to select from
    :param msg: the message to display on the input line
    :return option_selected: the selected item from the list
    """

    selection = 1
    count = len(options)
    if count > 1:
        display_options(options)
        selection = get_int_input(1, count, msg)
    option_selected = options[selection - 1][1]
    return option_selected


def display_options(options: list):
    print("\n")
    for index, option in enumerate(options):
        print(f"| {index+1} | {option[0]}")


def get_int_input(min: int, max: int, msg: str) -> int:
    """
    Makes a user select an integer between min & max stated values
    :param  min: the minimum acceptable integer value
    :param  max: the maximum acceptable integer value
    :param  msg: the message to display on the input line
    :return user_input: sanitised integer input in acceptable range
    """
    while True:
        try:
            user_input = int(input(f"{msg} (range {min} - {max}): "))
            if user_input not in range(min, max + 1):
                raise ValueError
            break
        except ValueError:
            print(
                "The value entered is not an integer in the acceptable"
                " range, please enter a different value!"
            )
            continue

    return user_input
