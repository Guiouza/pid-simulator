def isFloat(txt: str) -> bool:
    """
    Return true if is a float
    """
    try:
        float(txt)
        return True
    except ValueError:
        if txt == '-':
            return True
        return False


def isUnsignedFloat(txt: str) -> bool:
    """
    Return true only if is a float and positive
    """
    try:
        float(txt)
        return True
    except ValueError:
        return False
