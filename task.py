#!/usr/bin/env python3
#-*- coding: UTF-8 -*-


#* Prime decomposition * 15 minutes *

"""
Write a program to decompose the given integer, N, into a product of primes. Do
not solve the task using a built-in function that can accomplish the prime
number detection.

2 <= N <= 1000000

For example:

"""

from math import sqrt
from itertools import count
from functools import lru_cache


@lru_cache(128)
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(sqrt(n))):
        if not n % i:
            return False
    else:
        return True


def primes():
    for n in count(2):
        if is_prime(n):
            yield n


def decompose(n):
    rest = n
    factors = []
    for prime in primes():
        while not rest % prime:
            rest /= prime
            factors.append(prime)
            if rest == 1:
                break
    return tuple(factors)


def main():
    """
    The main function.
    """
    examples = [
        (24 , (2 , 2 , 2 , 3)),
        (19 , (19)),
        (10 , (2 , 5)),
        (70560 , (2 , 2 , 2 , 2 , 2 , 3 , 3 , 5 , 7 , 7)),
        (143848 , (2 , 2 , 2 , 17981)),
        (701711 , (701711)),
        (999999 , (3, 3 , 3 , 7 , 11 , 13 , 37)),
    ]
    for n, answer in examples:
        factors = decompose(n)
        print(n, factors)
        assert answer == factors


if __name__ == "__main__":
    exit(main())

