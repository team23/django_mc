from itertools import chain


def flatten(lists):
    return list(chain(*lists))
