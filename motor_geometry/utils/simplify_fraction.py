# motor_geometry/utils.py
from math import gcd

def simplify_fraction(numerator, denominator):
    """
    Rút gọn phân số numerator / denominator
    """
    common_divisor = gcd(numerator, denominator)
    return numerator // common_divisor, denominator // common_divisor
