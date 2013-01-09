#!/usr/bin/env python
# -*- coding: utf-8 -*-

# passtk

# Argument:
# -l/--level : 1-5, default is 3
# -n/--length : the length of the password # TODO

# level 1 : a-zA-Z
# level 2 : a-zA-Z0-9	(default)
# level 3 : a-zA-Z0-9!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

import argparse
import string
import random

digit = string.digits
lower = string.ascii_lowercase
upper = string.ascii_uppercase
letter = string.ascii_letters
punctuation = string.punctuation

str_1 = letter
str_2 = str_1 + digit
str_3 = str_2 + punctuation

def genstr(level):
	if level < 1:
		level = 1
	if level > 3:
		level = 3
	if level == 1:
		return str_1
	elif level == 2:
		return str_2
	else:
		return str_3

def generate(level=2):
	str = genstr(level)
	print ''.join(random.sample(str, 8))


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-l', '--level', dest='level', type=int, default=2,help='')
	args = parser.parse_args()
	
	level = args.level
	generate(level)
