# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com
"""
toml helper functions
 - python >= 3.11 has support for toml read.
"""
from typing import (Any, Dict)
import os
import tomllib as toml
from .utils import open_file


def read_toml_file(fpath: str) -> Dict[str, Any]:
    """
    read toml file and return a dictionary
    """
    this_dict: Dict[str, Any] = {}

    if os.path.exists(fpath):
        fobj = open_file(fpath, 'r')
        if fobj:
            data = fobj.read()
            fobj.close()
            this_dict = toml.loads(data)
    return this_dict
