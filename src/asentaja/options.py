# This file manages applying preset configurations

class Option:
    def __init__(self, description):
        self.description = description


_options = []


def register_option(option):
    _options.append(option)


def apply_options():
    for option in _options:
        option.apply()

