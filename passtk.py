#!/usr/bin/env python
# -*- coding: utf-8 -*-

# passtk

# Argument:
# -l/--level : 1-3, default is 2
# -n/--length : the length of the password

# level 1 : a-zA-Z
# level 2 : a-zA-Z0-9	(default)
# level 3 : a-zA-Z0-9!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

import argparse
import string
import random

DIGIT = string.digits
LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
LETTER = string.ascii_letters
PUNCTUATION = string.punctuation

def _filter(level):
	if level < 1:	level = 1
	if level > 3:	level = 3
	return level

def _shuffle(pwd):
	_pwd = list(pwd)
	random.shuffle(_pwd)
	return str().join(_pwd)


def choice_n(seq, n):
	# If use random.sample, the return is a set
	r_lst = list()
	for i in xrange(n):
		r_lst.append(random.choice(seq))
	return str().join(r_lst)


def gen_pass(level, length):
	lower_num = random.randint(1, length-level)
	lower_str = choice_n(LOWER, lower_num)

	upper_num = random.randint(1, length - lower_num-(level-1))
	upper_str = choice_n(UPPER, upper_num)

	pass_str = lower_str + upper_str

	if level > 1:
		if level == 2:
			digit_num = length - lower_num - upper_num
		else:
			digit_num = random.randint(1, length - lower_num - upper_num - (level-2))
		digit_str = choice_n(DIGIT, digit_num)
		pass_str += digit_str

	if level == 3:
		punc_num = length - lower_num - upper_num - digit_num
		punc_str = choice_n(PUNCTUATION, punc_num)
		pass_str += punc_str
	
	return pass_str
	

# Main Function
def generate(level=2, length=8):
	random.seed()
	pass_str = gen_pass(level, length)
	res = _shuffle(pass_str)
	print res


# Entry
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-l', '--level', dest='level', type=int, default=2, 
			help='The level(1-3, default is 2) of the password, higher is complex')
	parser.add_argument('-n', '--length', dest='length', type=int, default=8,
			help='The length of the password')
	args = parser.parse_args()
	
	level = _filter(args.level)
	length = args.length
	generate(level,length)
