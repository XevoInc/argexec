""" Default argexec parameter type options. """

from typing import Dict, Type, TypeVar

from dynamic_dispatch import dynamic_dispatch

T = TypeVar('T')


@dynamic_dispatch(default=True)
def argexec_param_options(typ: Type[T]) -> Dict:
    """
    Gets configuration parameters for argparse's add_argument given a type.

    :param typ: type to get parsing configuration for.
    :return: dictionary containing configuration.
    """
    # By default, all types have no configuration.
    return {}
