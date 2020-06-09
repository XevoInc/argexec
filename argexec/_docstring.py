""" Docstring parsing utilities. """

import inspect as _inspect
import re as _re
from typing import Callable, Dict, Optional, Tuple, Type

try:
    from typing import Final
except ImportError:
    from typing_extensions import Final


def get_type_name(type_: Type) -> str:
    return getattr(type_, '__name__', None) or getattr(type_, '_name', None) or repr(type_)


_PARAM_NAME_REGEX = _re.compile(r':param\s+(\w+)')


def parse_docstring(func: Callable) -> Tuple[Optional[str], Dict[str, str]]:
    """
    Parses docstrings into a function description and parameter descriptions.

    :param func: function to parse docstring of.
    :return: function description and
    """
    doc = _inspect.getdoc(func)
    params = {}

    if doc is None:
        return None, params

    desc = ''
    name = None
    for line in doc.splitlines():
        match = _re.match(_PARAM_NAME_REGEX, line)

        if match is not None:
            name = match.group(match.lastindex)
            params[name] = line[match.span(match.lastindex)[1] + 1:].strip()
        else:
            if line.startswith(':return') or line.startswith(':raises'):
                return desc, params

            if len(line) == 0:
                desc += '\n\n'
            if name is None:
                desc += line
            else:
                params[name] += line

    return desc, params
