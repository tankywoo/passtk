#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

def _filter(level, length):
    if level != max(min(level, 3), max(level, 1)):
        print "level range should be 1-3"
        level = max(min(level, 3), max(level, 1))
    if length != max(4, length):
        print "length range should at least 4"
        length = max(4, length)
    return (level, length)

def _shuffle(pwd):
    _pwd = list(pwd)
    random.shuffle(_pwd)
    return str().join(_pwd)

def _choice_n(seq, n):
    # different with random.sample(population, n)
    r_lst = list()
    for i in xrange(n):
        r_lst.append(random.choice(seq))
    return str().join(r_lst)

def _gen_pass(level, length):
    """
    :param level:
        lv1 : a-zA-Z
        lv2 : a-zA-Z0-9    (default)
        lv3 : a-zA-Z0-9!"#$%&"()*+,-./:;<=>?@[\]^_`{|}~
    """

    lower_num = random.randint(1, length-level)
    lower_str = _choice_n(LOWER, lower_num)
    if level == 1:
        upper_num = length - lower_num
    else:
        upper_num = random.randint(1, length - lower_num - (level - 1))
    upper_str = _choice_n(UPPER, upper_num)
    pass_str = lower_str + upper_str

    if level == 2 or level == 3:
        if level == 2:
            digit_num = length - lower_num - upper_num
        else:
            digit_num = random.randint(
                1, 
                length - lower_num - upper_num - (level - 2)
            )
        digit_str = _choice_n(DIGIT, digit_num)
        pass_str += digit_str

    if level == 3:
        punc_num = length - lower_num - upper_num - digit_num
        punc_str = _choice_n(PUNCTUATION, punc_num)
        pass_str += punc_str

    password = _shuffle(pass_str)
    return password


# Main Function
def main():
    parser = argparse.ArgumentParser(
            description="A tool to generate random password.")
    parser.add_argument("-l", "--level", dest="level", 
            type=int, default=DEFAULT_LEVEL, 
            help="The level(1-3, default is 2) of password, higher is complex")
    parser.add_argument("-n", "--length", dest="length", 
            type=int, default=DEFAULT_LENGTH,
            help="The length of password(at least 4, default is 8)")
    args = parser.parse_args()

    level, length = _filter(args.level, args.length)

    random.seed()
    password = _gen_pass(level, length)
    print password


if __name__ == "__main__":
    main()
