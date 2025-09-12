#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
TODO:

    * add --expire option, delete expire saved password entries
    * auto backup if program upgrade
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
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

DEFAULT_LEVEL = 2
DEFAULT_LENGTH = 8

# store password into ~/.passtk
PASS_STORE = os.path.join(os.path.expanduser('~'), '.passtk')

# 加密版本标识
ENCRYPT_MAGIC_V1 = 'PaSsTK EnCRYpt'  # 旧版ECB格式
ENCRYPT_MAGIC_V2 = 'PaSsTK-EnCRYpt-V2'   # 新版CBC格式
DECRYPT_MAGIC = ENCRYPT_MAGIC_V1[::-1]

# PBKDF2 配置
PBKDF2_ITERATIONS = 100000
SALT_SIZE = 16
IV_SIZE = 16

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

    def _color_print(self, msg, color, file=None):
        print(self.color_codes[color] + msg + self.color_codes["reset"], file=file)

    def print_ok(self, msg):
        self._color_print(msg, "green")

    def print_err(self, msg):
        self._color_print(msg, "red", file=sys.stderr)


class Cryptor(object):
    """
    加密解密类，支持新的CBC模式和旧的ECB模式向后兼容
    """

    @staticmethod
    def derive_key(password, salt):
        """使用PBKDF2派生256位密钥"""
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PBKDF2_ITERATIONS)

    @staticmethod
    def encrypt(secret_key, text):
        """使用AES-256-CBC加密（新版本）"""
        # 生成随机盐和IV
        salt = get_random_bytes(SALT_SIZE)
        iv = get_random_bytes(IV_SIZE)

        # 派生密钥
        key = Cryptor.derive_key(secret_key, salt)

        # 加密数据
        plaintext = (text + DECRYPT_MAGIC).encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

        # 组合：盐 + IV + 密文
        encrypted_data = salt + iv + ciphertext

        # 返回：版本标识 + base64编码的数据
        return ENCRYPT_MAGIC_V2 + base64.b64encode(encrypted_data).decode('utf-8')

    @staticmethod
    def decrypt(secret_key, text):
        """智能解密：自动检测版本并使用相应的解密方法"""
        if text.startswith(ENCRYPT_MAGIC_V2):
            return Cryptor._decrypt_cbc(secret_key, text)
        elif text.startswith(ENCRYPT_MAGIC_V1):
            return Cryptor._decrypt_ecb_legacy(secret_key, text)
        else:
            color.print_err("未知的加密格式")
            sys.exit()

    @staticmethod
    def _decrypt_cbc(secret_key, text):
        """解密CBC格式（新版本）"""
        try:
            # 移除版本标识
            encrypted_data = base64.b64decode(text[len(ENCRYPT_MAGIC_V2):])

            # 提取盐、IV和密文
            salt = encrypted_data[:SALT_SIZE]
            iv = encrypted_data[SALT_SIZE:SALT_SIZE + IV_SIZE]
            ciphertext = encrypted_data[SALT_SIZE + IV_SIZE:]

            # 派生密钥
            key = Cryptor.derive_key(secret_key, salt)

            # 解密
            cipher = AES.new(key, AES.MODE_CBC, iv)
            plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

            # 解码并验证
            plaintext_str = plaintext.decode('utf-8')
            if not plaintext_str.endswith(DECRYPT_MAGIC):
                color.print_err("密码错误")
                sys.exit()

            return plaintext_str[:-len(DECRYPT_MAGIC)]

        except Exception:
            color.print_err("密码错误或数据损坏")
            sys.exit()

    @staticmethod
    def _decrypt_ecb_legacy(secret_key, text):
        """解密ECB格式（旧版本，向后兼容）"""
        try:
            # 旧版填充方法
            def pad16(s):
                t = struct.pack('>I', len(s)) + s
                return t + b'\x00' * ((16 - len(t) % 16) % 16)

            def unpad16(s):
                n = struct.unpack('>I', s[:4])[0]
                return s[4:n + 4]

            # 旧版解密逻辑
            secret_key_padded = pad16(secret_key.encode('utf-8'))
            encrypted_text = text[len(ENCRYPT_MAGIC_V1):]

            cipher = AES.new(secret_key_padded, AES.MODE_ECB)
            decrypt_text = cipher.decrypt(base64.b64decode(encrypted_text))
            decrypt_text = unpad16(decrypt_text)

            decrypt_text_str = decrypt_text.decode('utf-8')

            if not decrypt_text_str.endswith(DECRYPT_MAGIC):
                color.print_err("密码错误")
                sys.exit()

            return decrypt_text_str[:-len(DECRYPT_MAGIC)]

        except Exception:
            color.print_err("密码错误或数据损坏")
            sys.exit()

    @staticmethod
    def is_encrypted(text):
        """检查文本是否已加密"""
        return text.startswith(ENCRYPT_MAGIC_V1) or text.startswith(ENCRYPT_MAGIC_V2)


class Password(object):
    """密码生成器类，支持不同复杂度级别的密码生成"""

    # 字符集定义
    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    DIGITS = string.digits
    PUNCTUATION = string.punctuation

    def __init__(self, length, level, exclude_ambiguous=False):
        """初始化密码生成器

        Args:
            length (int): 密码长度，至少4位
            level (int): 复杂度级别 1-3
            exclude_ambiguous (bool): 是否排除容易混淆的字符
        """
        self.length = length
        self.level = level
        self.exclude_ambiguous = exclude_ambiguous
        random.seed()

    def _validate_params(self):
        """验证参数有效性"""
        if self.length < 4:
            color.print_err("length should be at least 4")
            sys.exit()
        if not 1 <= self.level <= 3:
            color.print_err("level should be in 1-3")
            sys.exit()

    def _get_character_sets(self):
        """根据级别获取字符集

        Returns:
            list: 字符集列表
        """
        char_sets = [self.LOWERCASE, self.UPPERCASE]

        if self.level >= 2:
            char_sets.append(self.DIGITS)

        if self.level >= 3:
            char_sets.append(self.PUNCTUATION)

        # 如果需要排除混淆字符，则过滤掉这些字符
        if self.exclude_ambiguous:
            ambiguous_chars = 'Il1O0'
            char_sets = [''.join(c for c in char_set if c not in ambiguous_chars)
                         for char_set in char_sets]

        return char_sets

    def _distribute_length(self, num_sets):
        """将密码长度分配给各个字符集

        Args:
            num_sets (int): 字符集数量

        Returns:
            list: 每个字符集分配的字符数量
        """
        # 确保每个字符集至少有一个字符
        counts = [1] * num_sets
        remaining = self.length - num_sets

        # 随机分配剩余长度
        for _ in range(remaining):
            counts[random.randint(0, num_sets - 1)] += 1

        return counts

    def _generate_characters(self, char_sets, counts):
        """根据字符集和数量生成字符

        Args:
            char_sets (list): 字符集列表
            counts (list): 每个字符集的字符数量

        Returns:
            str: 生成的字符串
        """
        chars = []
        for char_set, count in zip(char_sets, counts):
            chars.extend(random.choices(char_set, k=count))

        # 打乱字符顺序
        random.shuffle(chars)
        return ''.join(chars)

    def generate(self):
        """生成密码

        Returns:
            str: 生成的密码

        复杂度级别说明:
            level 1: 小写字母 + 大写字母
            level 2: 小写字母 + 大写字母 + 数字 (默认)
            level 3: 小写字母 + 大写字母 + 数字 + 标点符号
        """
        self._validate_params()

        char_sets = self._get_character_sets()
        counts = self._distribute_length(len(char_sets))
        password = self._generate_characters(char_sets, counts)

        return password


def is_encrypted(f):
    """检查文件是否已加密（兼容函数）"""
    with open(f, 'r') as fd:
        ctx = fd.read()
    return Cryptor.is_encrypted(ctx)


def input_secret_key(input_msg=None, is_force=False):
    global secret_key
    if not is_force and secret_key:
        return
    secret_key = getpass.getpass(input_msg or "Input master password: ")


def display_entry(nid, entry):
    entry = entry.split('\t')
    if len(entry) == 2:  # without comment message
        entry.append('')
    date_str, password, comment = entry
    date_str = date_str.split('.')[0]  # remove microsecond
    ustr = ("%-6s\t%-19s\t%s\t%s" % (nid, date_str, password, comment))
    print(ustr)


color = Color()
cryptor = Cryptor()


def setup_argument_parser():
    """设置命令行参数解析器"""
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
    parser.add_argument("-c", dest="change", action='store_true',
                        help="Change master password")
    parser.add_argument("-e", "--exclude-ambiguous", dest="exclude_ambiguous",
                        action='store_true',
                        help="Exclude ambiguous characters (I, l, 1, 0, O)")
    return parser


def initialize_password_store():
    """初始化密码存储文件"""
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
            encrypt_text = cryptor.encrypt(secret_key, fd.read())
            fd.seek(0)
            fd.truncate()
            fd.write(encrypt_text)


def change_master_password():
    """修改主密码"""
    with open(PASS_STORE, 'r+') as fd:
        input_secret_key("Input old master password: ")
        decrypt_text = cryptor.decrypt(secret_key, fd.read())

        input_secret_key("Input new master password: ", is_force=True)
        secret_key_1st = secret_key
        input_secret_key("Input new master password again: ", is_force=True)
        if secret_key_1st != secret_key:
            color.print_err("new master passwords not match")
            sys.exit()
        encrypt_text = cryptor.encrypt(secret_key, decrypt_text)
        fd.seek(0)
        fd.truncate()
        fd.write(encrypt_text)
        color.print_ok("change master password ok")


def preview_passwords():
    """预览所有密码条目"""
    input_secret_key()
    with open(PASS_STORE, 'r') as fd:
        decrypt_text = cryptor.decrypt(secret_key, fd.read())
        entries = [e.rstrip() for e in decrypt_text.splitlines() if e.rstrip()]
        print("%-6s\t%-19s\t%s\t%s" % ('ID', 'DATE', 'PASSWORD', 'COMMENT'))
        for nid, entry in enumerate(entries, 1):
            display_entry(nid, entry)


def delete_password(del_id):
    """删除指定ID的密码条目"""
    input_secret_key()
    with open(PASS_STORE, 'r+') as fd:
        decrypt_text = cryptor.decrypt(secret_key, fd.read())
        entries = [e.rstrip() for e in decrypt_text.splitlines() if e.rstrip()]
        if del_id > len(entries):
            color.print_err("Delete id is greater than max entry id")
            sys.exit()
        display_entry(del_id, entries[del_id-1])
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


def generate_password(length, level, exclude_ambiguous):
    """生成密码"""
    p = Password(length, level, exclude_ambiguous)
    return p.generate()


def save_password(password, comment=None):
    """保存密码到存储文件"""
    now = datetime.datetime.now()
    stored_str = '{0}\t{1}'.format(now, password)
    if comment:
        stored_str += '\t{0}'.format(comment)
    stored_str += os.linesep

    with open(PASS_STORE, 'r+') as fd:
        input_secret_key("Input master password to save: ")
        decrypt_text = cryptor.decrypt(secret_key, fd.read())
        text = decrypt_text + stored_str  # last char is already os.linesep

        encrypt_text = cryptor.encrypt(secret_key, text)
        fd.seek(0)
        fd.truncate()
        fd.write(encrypt_text)


def main():
    parser = setup_argument_parser()
    args = parser.parse_args()

    initialize_password_store()

    if args.change:
        change_master_password()
        return

    if args.preview:
        preview_passwords()
        return

    if args.delete:
        delete_password(args.delete)
        return

    # 生成或添加密码
    if args.add:
        password = args.add
    else:
        password = generate_password(args.length, args.level, args.exclude_ambiguous)
        color.print_ok(password)

    # 保存密码（如果需要）
    if not args.unsave:
        save_password(password, args.comment)


if __name__ == "__main__":
    main()
