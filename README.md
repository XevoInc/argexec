# Argexec

![Build status](https://img.shields.io/github/workflow/status/XevoInc/argexec/Push%20CI/master)
[![PyPI](https://img.shields.io/pypi/v/argexec)](https://pypi.org/project/argexec/)
![PyPI - License](https://img.shields.io/pypi/l/argexec)

An unobtrusive, elegant mechanism to provide seamless command line interfaces through argparse for Python functions.
All you have to do is decorate your function of choice with `@argexec` and away you go!

## Features
* Description parsing from docstring
* Argument help parsing from reStructuredText-like docstrings
* Argument type enforcement via [typeguard](https://github.com/agronholm/typeguard) from 
  [type hints](https://www.python.org/dev/peps/pep-0484/)
* Argument default values from function signature
* Support for the following argument types:
  * All builtin primitives (`bool`, `int`, `float`, `str`, `bytes`)
  * Fixed length tuples of a supported type
  * Variable length tuples of a supported type
  * Lists of a supported type
* Extensible, complex custom type parsing via [`dynamic_dispatch`](https://github.com/XevoInc/dynamic_dispatch)

## Install

You may install this via the [`argexec`](https://pypi.org/project/argexec/) package on [PyPi](https://pypi.org):

```bash
pip3 install argexec
```

## Usage

The decorator may be applied to any Python function that meets the following requirements:
* Is not a member function
* Has [PEP 484](https://www.python.org/dev/peps/pep-0484/) type hints for all parameters
* Does not use `*args` or `**kwargs`

Example (`foo.py`):
```python
#!/usr/bin/python3

from typing import Tuple

from argexec import argexec
from argexec.types import LogLevel

@argexec
def _(w: int, x: Tuple[str, ...], y: LogLevel, z: bool = True):
    """
    Hello, world!

    :param w: foo.
    :param x: bar.
    :param y: baz.
    :param z: qux.
    """
    pass
```

```
$ ./foo.py --help
usage: foo.py [-h] [-y] [--no-z] w [x [x ...]]

Hello, world!

positional arguments:
  w           [int] foo
  x           [Tuple[str, ...]] bar

optional arguments:
  -h, --help  show this help message and exit
  -y, --y     [LogLevel=CRITICAL] baz (more flags for lower level)
  --no-z      [bool=True] qux
```



## Development

When developing, it is recommended to use Pipenv. To create your development environment:

```bash
pipenv install --dev
```

### Testing

TODO
