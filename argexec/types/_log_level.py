"""
Argexec parameter type for logging level.

This module serves as an example of how argexec's type configuration
system can be extended to support custom types.
"""

from argparse import Action, ArgumentParser, Namespace
from logging import getLevelName
from typing import Any, Dict, Optional, Sequence, Text, Union

from ._default import argexec_param_options


class LogLevel(int):
    """
    Type alias for int which can be used as a level for the logging package.

    Adds a command line flag that can be specified zero or more times, with each successive
    flag lowering the log level by 10. The default level is CRITICAL (50).
    """
    def __repr__(self):
        return getLevelName(self)

    # Note: all other maths involving LogLevels will return ints, not LogLevels. This is overridden
    # as we use left subtraction on log levels below. Other maths will require similar overrides.
    def __sub__(self, x: int) -> int:
        return self.__class__(super().__sub__(x))


class LogLevelAction(Action):
    """ Sets the level dest to the appropriate integer level based on the number of calls. """

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Union[Text, Sequence[Any], None],
                 option_string: Optional[Text] = ...) -> None:
        level = getattr(namespace, self.dest)
        setattr(namespace, self.dest, level - 10)


@argexec_param_options.dispatch(on=LogLevel)
def log_level_param_options() -> Dict:
    """ :returns: argparse options for LogLevel parameters. """
    return {
        'nargs': 0,
        'action': LogLevelAction,
        'required': False,
        'default': LogLevel(50),
        'help': ' (more flags for lower level)'
    }
