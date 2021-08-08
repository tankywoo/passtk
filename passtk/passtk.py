#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
TODO:

    * add --expire option, delete expire saved password entries
    * auto backup if program upgrade
'''
from __future__ import print_function
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

DEFAULT_LEVEL = 2
DEFAULT_LENGTH = 8

# store password into ~/.passtk
PASS_STORE = os.path.join(os.path.expanduser('~'), '.passtk')

ENCRYPT_MAGIC = 'PaSsTK EnCRYpt'
DECRYPT_MAGIC = ENCRYPT_MAGIC[::-1]

secret_key = None


class Color(object):
    color_codes = {
        "reset": "\033[0m",
        "black": "\033[1;30m",
        "red": "\033[1;31m",
        "green": "\033[1;32m",
        "yellow": "\033[1;33m",
        "blue": "\033[1;34m",
        "magenta": "\033[1;35m",
        "cyan": "\033[1;36m",
        "white": "\033[1;37m",
    }

    def _color_print(self, msg, color):
        print(self.color_codes[color] + msg + self.color_codes["reset"])

    def print_ok(self, msg):
        self._color_print(msg, "green")

    def print_err(self, msg):
        self._color_print(msg, "red")


class Cryptor(object):
    """
    https://paste.ubuntu.com/11024555/
    """
    @staticmethod
    def pad16(s):
        t = struct.pack('>I', len(s)) + s
        return t + b'\x00' * ((16 - len(t) % 16) % 16)

    @staticmethod
    def unpad16(s):
        n = struct.unpack('>I', s[:4])[0]
        return s[4:n + 4]

    @staticmethod
    def encrypt(secret_key, text):
        text = Cryptor.pad16((text + DECRYPT_MAGIC).encode('utf-8'))
        secret_key = Cryptor.pad16(secret_key.encode('utf-8'))

        cipher = AES.new(secret_key, AES.MODE_ECB)
        encrypt_text = ENCRYPT_MAGIC + base64.b64encode(cipher.encrypt(text)).decode('utf-8')
        return encrypt_text

    @staticmethod
    def decrypt(secret_key, text):
        secret_key = Cryptor.pad16(secret_key.encode('utf-8'))
        text = text[len(ENCRYPT_MAGIC):]

        cipher = AES.new(secret_key, AES.MODE_ECB)
        decrypt_text = cipher.decrypt(base64.b64decode(text))
        decrypt_text = Cryptor.unpad16(decrypt_text).decode('utf-8')

        if decrypt_text[-len(DECRYPT_MAGIC):] != DECRYPT_MAGIC:
            color.print_err("password invalid")
            sys.exit()

        return decrypt_text[:-len(DECRYPT_MAGIC)]


class Password(object):

    def __init__(self, length, level):
        self.length = length
        self.level = level
        self.password = ""
        random.seed()

    def valid(self):
        if self.length < 4:
            color.print_err("length should be at least 4")
            sys.exit()
        if self.level > 3 or self.level < 1:
            color.print_err("level should be in 1-3")
            sys.exit()

    def shuffle(self):
        pwd = list(self.password)
        random.shuffle(pwd)
        self.password = ''.join(pwd)

    @staticmethod
    def choice_n(seq, n):
        # different with random.sample(population, n)
        n_lst = [random.choice(seq) for _ in range(n)]
        return ''.join(n_lst)

    def generate(self):
        # pylint: disable=anomalous-backslash-in-string
        """
        :param level:
            level 1 : lower letters + upper letter
            level 2 : lower letters + upper letter + digits    (default)
            level 3 : lower letters + upper letter + digits + punctuations
        """
        self.valid()

        lower_num = random.randint(1, self.length-self.level)
        lower_str = self.choice_n(string.ascii_lowercase, lower_num)
        if self.level == 1:
            upper_num = self.length - lower_num
        else:
            upper_num = random.randint(1, self.length-lower_num-self.level+1)
        upper_str = self.choice_n(string.ascii_uppercase, upper_num)
        self.password += lower_str + upper_str

        if self.level in (2, 3):
            if self.level == 2:
                digit_num = self.length - lower_num - upper_num
            else:
                digit_num = random.randint(1, self.length-lower_num-upper_num-self.level+2)
            digit_str = self.choice_n(string.digits, digit_num)
            self.password += digit_str

        if self.level == 3:
            punc_num = self.length - lower_num - upper_num - digit_num
            punc_str = self.choice_n(string.punctuation, punc_num)
            self.password += punc_str

        self.shuffle()

        return self.password


def is_encrypted(f):
    with open(f, 'r') as fd:
        ctx = fd.read()
    if ctx[:len(ENCRYPT_MAGIC)] != ENCRYPT_MAGIC:
        return 0
    else:
        return 1


def input_secret_key(input_msg=None):
    global secret_key
    if not secret_key:
        secret_key = getpass.getpass(input_msg or "Input master password: ")


def display_entry(nid, entry):
    entry = entry.split('\t')
    if len(entry) == 2:  # without comment message
        entry.append('')
    date_str, password, comment = entry
    date_str = date_str.split('.')[0]  # remove microsecond
    print("%-6s\t%-19s\t%s\t%s" % (nid, date_str, password, comment))


color = Color()
cryptor = Cryptor()


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
    parser.add_argument("-d", dest="delete", type=int,
                        help="Delete password entries by id in ~/.passtk")
    parser.add_argument("-a", dest="add",
                        help="Add password manually into ~/.passtk")
    args = parser.parse_args()

    if not os.path.exists(PASS_STORE):
        print("{0} is not exists, create it".format(PASS_STORE))
        input_secret_key("Input new master password: ")
        with open(PASS_STORE, 'w') as fd:
            encrypt_text = cryptor.encrypt(secret_key, '')
            fd.write(encrypt_text)

    if not is_encrypted(PASS_STORE):
        print("{0} is not encrypted, encrypt it now".format(PASS_STORE))
        input_secret_key("Input new master password: ")
        with open(PASS_STORE, 'r+') as fd:
            encrypt_text = cryptor.cryptor.encrypt(secret_key, fd.read())
            fd.seek(0)
            fd.truncate()
            fd.write(encrypt_text)

    if args.preview:
        input_secret_key()
        with open(PASS_STORE, 'r') as fd:
            decrypt_text = cryptor.decrypt(secret_key, fd.read())
            entries = [e.rstrip() for e in decrypt_text.splitlines() if e.rstrip()]
            print("%-6s\t%-19s\t%s\t%s" % ('ID', 'DATE', 'PASSWORD', 'COMMENT'))
            for nid, entry in enumerate(entries, 1):
                display_entry(nid, entry)
        return

    if args.delete:
        del_id = args.delete
        input_secret_key()
        with open(PASS_STORE, 'r+') as fd:
            decrypt_text = cryptor.decrypt(secret_key, fd.read())
            entries = [e.rstrip() for e in decrypt_text.splitlines() if e.rstrip()]
            if del_id > len(entries):
                color.print_err("Delete id is greater than max entry id")
                sys.exit()
            display_entry(del_id, entries[del_id-1])
            try:
                ans = raw_input('Delete it? (y/N) ')
            except NameError:  # py3
                ans = input('Delete it? (y/N) ')
            if ans.lower() not in ('y', 'yes'):
                return
            entries = entries[:del_id-1] + entries[del_id:]
            decrypt_text = os.linesep.join(entries) + os.linesep
            encrypt_text = cryptor.encrypt(secret_key, decrypt_text)
            fd.seek(0)
            fd.truncate()
            fd.write(encrypt_text)
            color.print_ok('delete done')
        return

    if args.add:
        password = args.add
    else:
        p = Password(args.length, args.level)
        password = p.generate()
        color.print_ok(password)

    unsave = args.unsave
    if unsave:
        return

    now = datetime.datetime.now()
    stored_str = '{0}\t{1}'.format(now, password)
    if args.comment:
        stored_str += '\t{0}'.format(args.comment)
    stored_str += os.linesep

    with open(PASS_STORE, 'r+') as fd:
        input_secret_key("Input master password to save: ")
        decrypt_text = cryptor.decrypt(secret_key, fd.read())
        text = decrypt_text + stored_str  # last char is already os.linesep

        encrypt_text = cryptor.encrypt(secret_key, text)
        fd.seek(0)
        fd.truncate()
        fd.write(encrypt_text)


if __name__ == "__main__":
    main()
