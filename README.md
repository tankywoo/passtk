A tool to generate random password, and the generated password entries will be stored into `~/.passtk` file for backup.

## Usage ##

    usage: passtk [-h] [-l LEVEL] [-n LENGTH] [-m COMMENT] [-u] [-p]

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



## Installation ##

    pip install passtk

or

    python setup.py install

## Contact ##

    Tanky Woo<me@tankywoo.com>

