#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
TODO:

    * add --expire option, delete expire saved password entries
'''
import os
import sys
import datetime
import argparse
import string
import random
import struct
import base64
import getpass
from Crypto.Cipher import AES

DIGIT = string.digits
LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
PUNCTUATION = string.punctuation

DEFAULT_LEVEL = 2
DEFAULT_LENGTH = 8

# store password into ~/.passtk
PASS_STORE = os.path.join(os.path.expanduser('~'), '.passtk')

ENCRYPT_MAGIC = 'PaSsTK EnCRYpt'
DECRYPT_MAGIC = ENCRYPT_MAGIC[::-1]

secret_key = None


def is_encrypted(f):
    with open(f, 'r') as fd:
        ctx = fd.read()
    if ctx[:len(ENCRYPT_MAGIC)] != ENCRYPT_MAGIC:
        return 0
    else:
        return 1


def input_secret_key():
    global secret_key
    if not secret_key:
        secret_key = getpass.getpass("INPUT PASSWORD: ")


# https://paste.ubuntu.com/11024555/
def pad16(s):
    t = struct.pack('>I', len(s)) + s
    return t + '\x00' * ((16 - len(t) % 16) % 16)


def unpad16(s):
    n = struct.unpack('>I', s[:4])[0]
    return s[4:n + 4]


def encrypt(secret_key, text):
    text = pad16(text + DECRYPT_MAGIC)
    secret_key = pad16(secret_key)

    cipher = AES.new(secret_key, AES.MODE_ECB)
    encrypt_text = ENCRYPT_MAGIC + base64.b64encode(cipher.encrypt(text))
    return encrypt_text


def decrypt(secret_key, text):
    secret_key = pad16(secret_key)
    text = text[len(ENCRYPT_MAGIC):]

    cipher = AES.new(secret_key, AES.MODE_ECB)
    decrypt_text = cipher.decrypt(base64.b64decode(text))
    decrypt_text = unpad16(decrypt_text)

    if decrypt_text[-len(DECRYPT_MAGIC):] != DECRYPT_MAGIC:
        print("password invalid")
        sys.exit()

    return decrypt_text[:-len(DECRYPT_MAGIC)]


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
    parser.add_argument("-m", "--comment", dest="comment",
                        help="Add comment for password")
    parser.add_argument("-u", "--unsave", dest="unsave",
                        action='store_true',
                        help="Disable storing password into ~/.passtk")
    parser.add_argument("-p", dest="preview", action='store_true',
                        help="Show password entries in ~/.passtk")
    args = parser.parse_args()

    if not os.path.exists(PASS_STORE):
        print("{0} is not exists, create it".format(PASS_STORE))
        input_secret_key()
        with open(PASS_STORE, 'w') as fd:
            encrypt_text = encrypt(secret_key, '')
            fd.write(encrypt_text)

    if not is_encrypted(PASS_STORE):
        print("{0} is not encrypted, encrypt it now".format(PASS_STORE))
        input_secret_key()
        with open(PASS_STORE, 'r+') as fd:
            encrypt_text = encrypt(secret_key, fd.read())
            fd.seek(0)
            fd.truncate()
            fd.write(encrypt_text)

    if args.preview:
        input_secret_key()
        with open(PASS_STORE, 'r') as fd:
            decrypt_text = decrypt(secret_key, fd.read())
            for entry in decrypt_text.splitlines():
                print(entry.rstrip())
        return

    level, length = _filter(args.level, args.length)

    random.seed()
    password = _gen_pass(level, length)
    print password

    unsave = args.unsave
    if unsave:
        return

    now = datetime.datetime.now()
    stored_str = '{0}\t{1}'.format(now, password)
    if args.comment:
        stored_str += '\t{0}'.format(args.comment)
    stored_str += os.linesep

    with open(PASS_STORE, 'r+') as fd:
        input_secret_key()
        decrypt_text = decrypt(secret_key, fd.read())
        text = decrypt_text + stored_str  # last char is already os.linesep

        encrypt_text = encrypt(secret_key, text)
        fd.seek(0)
        fd.truncate()
        fd.write(encrypt_text)


if __name__ == "__main__":
    main()
