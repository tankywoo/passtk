A command line tool to generate random password.

The generated password entries will be stored into `~/.passtk` file. Like [1Password](https://1password.com/) / [LastPass](https://www.lastpass.com/) / ..., there is a **master password** to manage `~/.passtk`.

## Usage

```
usage: passtk.py [-h] [-l LEVEL] [-n LENGTH] [-m COMMENT] [-u] [-p]
                 [-d DELETE]

A tool to generate random password.

optional arguments:
  -h, --help            show this help message and exit
  -l LEVEL, --level LEVEL
                        The level(1-3, default is 2) of password, higher is
                        complex
  -n LENGTH, --length LENGTH
                        The length of password(at least 4, default is 8)
  -m COMMENT, --comment COMMENT
                        Add comment for password
  -u, --unsave          Disable storing password into ~/.passtk
  -p                    Show password entries in ~/.passtk
  -d DELETE             Delete password entries by id in ~/.passtk
  -c CHANGE             Change master password
```

## Encryption Algorithm Upgrade

Starting from v0.6.6, passtk uses a more secure AES-256-CBC + PBKDF2 encryption algorithm to replace the old ECB mode.

If you want to immediately upgrade your existing password store to the new encryption format, you can trigger the upgrade by adding a temporary password:

```bash
passtk.py -a "temp" -m "Temporary password for encryption format upgrade"

# Delete the temporary password after upgrade is complete
passtk.py -p
passtk.py -d <temporary_password_ID>
```


## Installation

```
pip install -U passtk
```

or

```
python setup.py install
```


## License

MIT License


## Contact

Tanky Woo <me@tankywoo.com>
