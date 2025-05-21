# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com
"""
Set process priority
"""
# pylint: disable=too-few-public-methods
import psutil
from psutil import (IOPRIO_CLASS_NONE, IOPRIO_CLASS_RT, IOPRIO_CLASS_BE)
from psutil import (IOPRIO_CLASS_IDLE)


class Prio:
    """
    set nice and ionice
    """
    def __init__(self,
                 nice: int = 15,
                 ionice_class: int = 3,
                 ionice_level: int = 6
                 ):

        self.nice = nice if nice is not None else 15
        self.ionice_class = ionice_class if ionice_class is not None else 3
        self.ionice_level = ionice_level if ionice_level is not None else 6

        self._check_values()

    def set_prio(self, pid: int = -1):
        """
        Set the current values
        """
        if pid > 1:
            proc = psutil.Process(pid=pid)
        else:
            proc = psutil.Process()

        args = self._ionice_args()
        try:
            proc.nice(self.nice)
            proc.ionice(**args)
        except psutil.Error:
            pass

    def _ionice_args(self):
        """
        return dictionary psutil.ionice args
         - map ionice_class to enum
         {ioclass=None, value=None)
        """
        ionice_arg = {}
        match self.ionice_class:
            case 0:
                ionice_arg = {'ioclass': IOPRIO_CLASS_NONE}

            case 1:
                ionice_arg = {'ioclass': IOPRIO_CLASS_RT,
                              'value:': self.ionice_level}

            case 2:
                ionice_arg = {'ioclass': IOPRIO_CLASS_BE,
                              'value':  self.ionice_level}

            case 3:
                ionice_arg = {'ioclass': IOPRIO_CLASS_IDLE}

            case _:
                ionice_arg = {'ioclass': IOPRIO_CLASS_NONE}

        return ionice_arg

    def _check_values(self):
        """
        ensure valid (io)nice values
        """
        self.nice = _range_limit(self.nice, -20, 20)

        self.ionice_class = _range_limit(self.ionice_class, 0, 3)
        self.ionice_level = _range_limit(self.ionice_level, 0, 7)


def _range_limit(value: int, low: int, high: int) -> int:
    """
    Limits integer number to fall in the specified range.

    Args:
        value: The number to limit.
        low: The minimum allowed value.
        high: The maximum allowed value.

    Returns:
        The range bound result
    """
    range_bound = max(min(value, high), low)
    return range_bound
