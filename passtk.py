#!/usr/bin/env python
# -*- coding: utf-8 -*-

# passtk

# Argument:
# -l/--level : 1-5, default is 3
# -n/--length : the length of the password # TODO

# level 1 : a-zA-Z
# level 2 : a-zA-Z0-9	(default)
# level 3 : a-zA-Z0-9!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~


# Base : lower + power

import argparse
import string
import random

digit = string.digits
lower = string.ascii_lowercase
upper = string.ascii_uppercase
letter = string.ascii_letters
punctuation = string.punctuation


def generate(level=2):
	#str = genstr(level)
	#print ''.join(random.sample(str, 8))
	str=''
	if level == 1:
		res =  ''.join(random.sample(letter, 8))
	elif level == 2:
		s1 = ''.join(random.sample(letter,7))
		s2 = random.choice(digit)
		res = s1+s2
	else:
		s1 = ''.join(random.sample(letter,6))
		s2 = ''.join(random.sample(digit+punctuation,2))
		res = s1+s2
	res2 = list(res)
	random.shuffle(res2)
	res3 = ''.join(res2)
	print res3


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-l', '--level', dest='level', type=int, default=2,help='')
	args = parser.parse_args()
	
	level = args.level
	generate(level)
