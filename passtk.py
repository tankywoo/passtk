#!/usr/bin/env python
# -*- coding: utf-8 -*-

# passtk

# Argument:
# -l/--level : 1-5, default is 3
# -n/--length : the length of the password

# level 1 : a-z
# level 2 : a-zA-Z
# level 3 : a-zA-Z0-9	(default)
# level 4 : a-zA-Z0-9~!@#$%^&*
# level 5 : a-zA-Z0-9!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

import argparse
import string

digit = string.digits
lower = string.lowercase
upper = string.uppercase
punctuation_1 = '~!@#$%^&*'
punctuation_2 = string.punctuation


def generate():
	pass


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-l', '--level', dest='level', default=3,help='')
	args = parser.parse_args()
