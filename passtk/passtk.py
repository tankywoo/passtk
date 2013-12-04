#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
usage: passtk.py [-h] [-l LEVEL] [-n LENGTH]

A tool to generate random password.

optional arguments:
  -h, --help            show this help message and exit
  -l LEVEL, --level LEVEL
                        The level(1-3, default is 2) of password, higher is
                        complex
  -n LENGTH, --length LENGTH
                        The length of password


* level 1 : a-zA-Z
* level 2 : a-zA-Z0-9    (default)
* level 3 : a-zA-Z0-9!"#$%&"()*+,-./:;<=>?@[\]^_`{|}~

"""

import argparse
import string
import random

DIGIT = string.digits
LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
LETTER = string.ascii_letters
PUNCTUATION = string.punctuation

DEFAULT_LEVEL = 2
DEFAULT_LENGTH = 8

def _filter(level):
    if level < 1:    level = 1
    if level > 3:    level = 3
    return level

def _shuffle(pwd):
    _pwd = list(pwd)
    random.shuffle(_pwd)
    return str().join(_pwd)

def _choice_n(seq, n):
    # If use random.sample, the return is a set
    r_lst = list()
    for i in xrange(n):
        r_lst.append(random.choice(seq))
    return str().join(r_lst)

def _gen_pass(level, length):
    lower_num = random.randint(1, length-level)
    lower_str = _choice_n(LOWER, lower_num)

    if level == 1:
        upper_num = length - lower_num
    else:
        upper_num = random.randint(1, length - lower_num-(level-1))
    upper_str = _choice_n(UPPER, upper_num)

    pass_str = lower_str + upper_str

    if level > 1:
        if level == 2:
            digit_num = length - lower_num - upper_num
        else:
            digit_num = random.randint(1, length - lower_num - upper_num - (level-2))
        digit_str = _choice_n(DIGIT, digit_num)
        pass_str += digit_str

    if level == 3:
        punc_num = length - lower_num - upper_num - digit_num
        punc_str = _choice_n(PUNCTUATION, punc_num)
        pass_str += punc_str

    return pass_str


# Main Function
def main():
    parser = argparse.ArgumentParser(
            description="A tool to generate random password.")
    parser.add_argument("-l", "--level", dest="level", 
            type=int, default=DEFAULT_LEVEL, 
            help="The level(1-3, default is 2) of password, higher is complex")
    parser.add_argument("-n", "--length", dest="length", 
            type=int, default=DEFAULT_LENGTH,
            help="The length of password")
    args = parser.parse_args()

    level = _filter(args.level)
    length = args.length

    random.seed()
    pass_str = _gen_pass(level, length)
    password = _shuffle(pass_str)
    print password


if __name__ == "__main__":
    main()
