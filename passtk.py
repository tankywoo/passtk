#!/usr/bin/env python
# -*- coding: utf-8 -*-

# passtk

# Argument:
# -l/--level : 1-3, default is 2
# -n/--length : the length of the password # TODO

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


def shuffle(pwd):
	_pwd = list(pwd)
	random.shuffle(_pwd)
	return ''.join(_pwd)


def level_one(length):
	lower_num = random.randint(1,length-1)
	lower_str = str().join(random.sample(LOWER, lower_num))
	upper_num = length - lower_num
	upper_str = str().join(random.sample(UPPER, upper_num))
	pass_str = lower_str + upper_str
	return pass_str


def level_two(length):
	lower_num = random.randint(1,length-2)
	lower_str = str().join(random.sample(LOWER, lower_num))
	upper_num = random.randint(1,length - lower_num-1)
	upper_str = str().join(random.sample(UPPER, upper_num))
	digit_num = length - lower_num - upper_num
	digit_str = str().join(random.sample(DIGIT, digit_num))
	pass_str = lower_str + upper_str + digit_str
	return pass_str


def level_three(length):
	lower_num = random.randint(1,length-3)
	lower_str = str().join(random.sample(LOWER, lower_num))
	upper_num = random.randint(1,length - lower_num-2)
	upper_str = str().join(random.sample(UPPER, upper_num))
	digit_num = random.randint(1,length - lower_num - upper_num - 1)
	digit_str = str().join(random.sample(DIGIT, digit_num))
	punc_num = random.randint(1,length - lower_num - upper_num - digit_num)
	punc_str = str().join(random.sample(PUNCTUATION, punc_num))
	pass_str = lower_str + upper_str + digit_str + punc_str
	return pass_str

	
def generate(level=2, length=8):
	random.seed()
	if level == 1:
		pass_str = level_one(length)
	elif level == 2:
		pass_str = level_two(length)
	else:
		pass_str = level_three(length)
	res = shuffle(pass_str)
	print res


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-l', '--level', dest='level', type=int, default=2, 
			help='The level(1-3, default is 2) of the password, higher is complex')
	parser.add_argument('-n', '--length', dest='length', type=int, default=8,
			help='The length of the password')
	args = parser.parse_args()
	
	level = args.level
	length = args.length
	generate(level,length)
