def nearst_odd(n: int):
    """
    Returns the greatest odd number less than the given number
    """
    if n & 1:
        return n
    return n-1

def map_pos(pos: int, width: int) -> int:
    x = pos
    if x > 100:
        x = 100
    elif x < -100:
        x = -100
    
    pos_mapped = x*(width - 1)/200 + (width+1)/2
    return round(pos_mapped)
