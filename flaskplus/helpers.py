from collections import namedtuple


def create_namedtuple(name, *values):
    return namedtuple(name, values)(*values)



