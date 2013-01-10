Passtk is a `python` script that can generate a `random password`.
Copyright (C) 2013 by TankyWoo

Usage:

It can specified the `level` and the `length` of the password

	usage: passtk.py [-h] [-l LEVEL] [-n LENGTH]

	optional arguments:
	  -h, --help            show this help message and exit
	  -l LEVEL, --level LEVEL
							The level(1-3, default is 2) of the password, higher
							is complex
	  -n LENGTH, --length LENGTH
							The length of the password

Setup:

Use it in your `Unix/Linux` system:
	sudo cp passtk.py /usr/bin/passtk
And then you can use `passtk` command to use it.

MIT License

Contact:
	echo YWRtaW5AdGFua3l3b28uY29tCg== | base64 -d
