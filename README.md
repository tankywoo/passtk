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
