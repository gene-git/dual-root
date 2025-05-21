# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com
"""
Read sync daemon confix file
"""
from typing import (Any, Dict, List, Sequence)
from .toml import read_toml_file

from ._types import SyncListElem


def _elem_to_src_dst(item) -> SyncListElem:
    """
    Put in standard format:
     [source, [destination(s)], exclusions]
     exclusions are options.
     dest may be string or list
    """
    src_dst_excl: SyncListElem = ('', [], [])

    if isinstance(item, list):

        src: str = item[0]

        dst: List[str]
        if isinstance(item[1], list):
            dst = item[1]
        else:
            dst = [item[1]]

        excl: List[str] = []
        if len(item) > 2:
            excl = item[2]

        src_dst_excl = (src, dst, excl)

    return src_dst_excl


def _parse_sync_list(item: Sequence[str | List[str]]) -> List[SyncListElem]:
    """
    Takes conf file input and maps it to
    list of (src, dst, excl)

    Input file contains sync_list of form:
       [
       [src, dst, excl],
       [src, dst, excl],
       ]
    """
    sync_list: List[SyncListElem] = []

    if not item or not isinstance(item, list):
        return sync_list

    # num_elems = len(item)
    #
    # (src, dst, excl)
    # src: is always path str so never a list.
    #
    if isinstance(item[0], list):
        for subitem in item:
            if isinstance(subitem, list):
                sync_list += _parse_sync_list(subitem)
    else:
        src_dst_excl = _elem_to_src_dst(item)
        sync_list.append(src_dst_excl)

    return sync_list


def _set_val(key: str, conf_file: Dict[str, Any], conf: Dict[str, Any]):
    """
    Use value from file if set
    """
    val = conf_file.get(key)
    if val is not None:
        conf[key] = val


def read_config(config_file) -> Dict[str, Any]:
    """
    Read any sync daemon config
    Keys:
      - dualroot = bool
      - sync = sync list
        list of source,dest,exclusions
        exclusions are optional, and dest can be a list
    """
    conf_file = read_toml_file(config_file)

    #
    # ionice default: none,0
    #   - class: idle(3), none(0), best-effort(2), realtime(1)
    #   - level: 0-7 (0=highest) for realtime and best-effort only
    # sync_delay - seconds between pending rsync requests
    sync_list: List[SyncListElem] = []
    rsync_opts: List[str] = ["-axHAXt"]
    conf = {
            'dualroot': True,
            'rsync_opts': rsync_opts,
            'nice': 19,
            'ionice_class': 3,         # 0=idle
            'ionice_level': 6,
            'sync_delay': 300,
            'sync_list': sync_list,
            }

    if conf_file:
        _set_val('dualroot', conf_file, conf)
        _set_val('nice', conf_file, conf)
        _set_val('ionice_class', conf_file, conf)
        _set_val('ionice_level', conf_file, conf)
        _set_val('sync_delay', conf_file, conf)

        #
        # rsync_opts string -> list
        #
        val = conf_file.get('rsync_opts')
        if val is not None:
            conf['rsync_opts'] = val.split()

        #
        # sync is a list, where each element is a list:
        #   [source, dest] or [source, dest, excludes]
        # dest is a path string or list of paths
        # excludes is a list of strings.
        # Map to list of tuples:
        #   (src: str, dst: List[stre], exclude: List[str])
        #
        val = conf_file.get('sync')
        if val is not None:
            conf['sync_list'] = _parse_sync_list(val)

    return conf
