# Compression gigabyte data
Textual information compression program written with Python3 by Gerardas Martynovas.
Additionally this repository holds tools used for some of analysis and tests.

# Prerequisites
Only prerequisite is Python with at least 3.5 version.
All python files found in this repository are tested with Python 3.6 only.

# Usage
On either unix or windows machine you can check help by typing this to your terminal:
```
$ python3 HuffmanPartial.py -h
```

# Examples
To compress file with name test.txt and output compressed archive to current directory type:
```
$ python3 HuffmanPartial.py -f test.txt -o . -e
```

To decompress product of previous command use:
```
$ python3 HuffmanPartial.py -f test.gm -o . -d
```

