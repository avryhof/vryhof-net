def python3_cmp(x, y):
    """
    Compare the two objects x and y and return an integer according to the outcome.
    The return value is negative if x < y, zero if x == y and strictly positive if x > y.
    """
    retn = None

    try:
        if x is None and y is None:
            retn = 0
        elif x is None:
            retn = -1
        elif y is None:
            retn = 1
        elif x < y:
            retn = -1
        elif x == y:
            retn = 0
        elif x > y:
            retn = 1
    except TypeError:
        print("x: %s %s | y: %s %s" % (x, type(x), y, type(y)))

    return retn
