#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
TODO:

    * add --expire option, delete expire saved password entries
'''
import os
import datetime
import argparse
import string
import random

DIGIT = string.digits
LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
PUNCTUATION = string.punctuation

DEFAULT_LEVEL = 2
DEFAULT_LENGTH = 8

# store password into ~/.passtk
PASS_STORE = os.path.join(os.path.expanduser('~'), '.passtk')


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
    return ''.join(_pwd)


def _choice_n(seq, n):
    # different with random.sample(population, n)
    n_lst = [random.choice(seq) for _ in xrange(n)]
    return ''.join(n_lst)


def _gen_pass(level, length):
    # pylint: disable=anomalous-backslash-in-string
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
        upper_num = random.randint(1, length-lower_num-level+1)
    upper_str = _choice_n(UPPER, upper_num)
    pass_str = lower_str + upper_str

    if level in (2, 3):
        if level == 2:
            digit_num = length - lower_num - upper_num
        else:
            digit_num = random.randint(1, length-lower_num-upper_num-level+2)
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
                        help="The level(1-3, default is %s) of password,"
                             " higher is complex" % DEFAULT_LEVEL)
    parser.add_argument("-n", "--length", dest="length",
                        type=int, default=DEFAULT_LENGTH,
                        help="The length of password(at least 4, "
                             "default is %s)" % DEFAULT_LENGTH)
    parser.add_argument("-u", "--unsave", dest="unsave",
                        action='store_true',
                        help="Disable storing password into ~/.passtk")
    parser.add_argument("-p", dest="preview", action='store_true',
                        help="Show password entries in ~/.passtk")
    args = parser.parse_args()

    if args.preview:
        if os.path.exists(PASS_STORE):
            with open(PASS_STORE, 'r') as fd:
                for entry in fd.xreadlines():
                    print(entry.rstrip())
        else:
            print('{0} file not exists'.format(PASS_STORE))
        return

    level, length = _filter(args.level, args.length)

    random.seed()
    password = _gen_pass(level, length)
    print password

    unsave = args.unsave
    if not unsave:
        with open(PASS_STORE, 'a+') as fd:
            now = datetime.datetime.now()
            stored_str = '{0}\t{1}\n'.format(now, password)
            fd.write(stored_str)


if __name__ == "__main__":
    main()
