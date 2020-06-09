""" Decorator for automatic argument parsing and execution of python functions. """

import argparse as _argparse
import inspect as _inspect
from typing import Callable, Sequence, TypeVar

from typeguard import check_type, typechecked

try:
    from typing import get_args, get_origin
except ImportError:
    # Python <3.8.
    from typing_extensions import get_args, get_origin

from ._docstring import get_type_name, parse_docstring
from .types import argexec_param_options


@typechecked
def argexec(func: Callable):
    """
    Builds automatic argument parser for the given function and calls it.

    Custom type parsing and argument configuration may be added using types from the argexec.types module.

    :param func: function to execute.
    """
    description, params = parse_docstring(func)
    parser = _argparse.ArgumentParser(description=description, formatter_class=_argparse.RawTextHelpFormatter)

    sequences = {}

    sig = _inspect.signature(func)
    for name, arg in sig.parameters.items():
        type_ = arg.annotation
        if type_ == _inspect.Parameter.empty:
            raise TypeError('argexec requires all parameters be type annotated')
        parameters = {}

        # Parameters are required if they have no default value.
        required = arg.default == _inspect.Parameter.empty

        # Infer argument type and nargs for generic typed parameters.
        origin = get_origin(type_)
        if origin is None:
            type_name = get_type_name(type_)
        else:
            type_name = repr(type_).replace('typing.', '')
            if issubclass(origin, Sequence) and not origin == str:
                if origin == tuple:
                    kwargs = get_args(type_)

                    if len(kwargs) == 0:
                        # Empty tuple type.
                        parameters['nargs'] = 0
                        if not required:
                            parameters['default'] = ()
                    elif len(kwargs) >= 1:
                        parameters['type'] = kwargs[0]

                        if len(kwargs) == 1:
                            # One-element tuple.
                            parameters['nargs'] = 1
                        elif len(kwargs) == 2 and kwargs[1] == Ellipsis:
                            # Variable-length tuple of one type.
                            parameters['nargs'] = '*'
                            if not required:
                                parameters['default'] = ()
                        elif kwargs[-1] == Ellipsis:
                            raise TypeError('variable length tuples with ellipses are not supported')
                        elif not all(kwarg != kwargs[0] for kwarg in kwargs[1:]):
                            # Fixed-length tuple with more than one type.
                            raise TypeError('multi-type tuples are not supported')
                        else:
                            # Fixed length tuple with one type.
                            parameters['nargs'] = len(kwargs)
                else:
                    parameters['nargs'] = '*'
                    parameters['default'] = origin

                    kwargs = get_args(type_)
                    if len(kwargs) > 1:
                        raise TypeError(f'multi-type generics for {type_} are not supported')
                    if not isinstance(kwargs[0], TypeVar):
                        parameters['type'] = kwargs[0]
                sequences[name] = origin
            else:
                raise TypeError(f'unsupported generic type {origin}')

        # Get type-specific information.
        type_config = argexec_param_options(type_)

        # Merge type-specific config into inferred config.
        parameters.update(type_config)
        required = parameters.get('required', required)

        # Enforce default value.
        if not required and arg.default != _inspect.Parameter.empty:
            parameters['default'] = arg.default
        try:
            default = parameters['default']
            if default is not None:
                check_type('default', default, type_)
        except KeyError:
            pass

        # Populate help field with inferred description.
        help_ = params.get(arg.name, "")
        if help_.endswith('.'):
            # Periods at the end are unsightly.
            help_ = help_[:-1]

        # Get the default value to put next to argument type.
        try:
            default = f'={parameters["default"]!r}'
        except KeyError:
            default = ''
        parameters['help'] = f'[{type_name}{default}] {help_}{type_config.pop("help", "")}'

        # Set type name to nice string.
        if 'type' not in parameters:
            parameters['type'] = type_
        elif not hasattr(parameters['type'], '__name__'):
            parameters['type'].__name__ = type_name

        # Determine flag names and set requirement if necessary.
        if arg.kind == _inspect.Parameter.KEYWORD_ONLY or \
                (arg.kind == _inspect.Parameter.POSITIONAL_OR_KEYWORD and not required):
            if type_ == bool and not required:
                # Boolean flag argument.
                del parameters['type']
                if arg.default:
                    parameters['action'] = 'store_false'
                    names = (f'--no-{name}',)
                else:
                    parameters['action'] = 'store_true'
                    names = (f'--{name}',)
            else:
                # Normal flag argument.
                names = (f'-{name[0]}', f'--{name}')
                parameters['required'] = required
        else:
            names = (name,)

        parser.add_argument(*names, **parameters)

    parsed = parser.parse_args()

    kwargs = vars(parsed)
    for name, arg in kwargs.items():
        if name in sequences:
            kwargs[name] = sequences[name](arg)

    args = []
    for name, arg in sig.parameters.items():
        if arg.kind == _inspect.Parameter.POSITIONAL_ONLY:
            if name in kwargs:
                args.append(kwargs.pop(name))

    func(*args, **kwargs)

    return func
