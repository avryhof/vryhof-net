def is_empty(value):
    return value in [0, False, None, "", {}, []]


def make_list(thing_that_should_be_a_list):
    """If it is not a list.  Make it one. Return a list."""
    if thing_that_should_be_a_list is None:
        thing_that_should_be_a_list = []

    if not isinstance(thing_that_should_be_a_list, list):
        thing_that_should_be_a_list = [thing_that_should_be_a_list]

    return thing_that_should_be_a_list
