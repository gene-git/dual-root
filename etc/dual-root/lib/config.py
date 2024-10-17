# SPDX-License-Identifier: MIT
# Copyright (c) 2023, Gene C
"""
Read sync daemon confix file
"""

from .toml import read_toml_file

def _elem_to_src_dst(item):
    """
    Put in standard format:
     [source, [destination(s)], exclusions]
     exclusions are options.
     dest may be string or list
    """
    src_dst_excl = None
    if isinstance(item, list):
        src = item[0]
        dst = item[1]
        excl = []
        if len(item) > 2:
            excl = item[2]
        if not isinstance(dst,list):
            dst = [dst]
        src_dst_excl = [src, dst, excl]
    return src_dst_excl

def _parse_sync_list(item, sync_list):
    """
    Takes conf file input and maps it to
    list of [src_dst, src_dst]
    With src_dst ~ [src, [dst_list]]
    """
    if not item:
        return

    if not isinstance(item, list):
        return

    num_elems = len(item)
    #
    # [src, dst, excl]
    # src: is never a list.
    #
    item_0_is_list = isinstance(item[0], list)
    if not item_0_is_list and num_elems in (2,3) :
        src_dst_excl = _elem_to_src_dst(item)
        sync_list.append(src_dst_excl)
    else:
        for subitem in item:
            _parse_sync_list(subitem, sync_list)


def _set_val(key:str, conf_file:dict, conf:dict):
    ''' Use value from file if set '''
    val = conf_file.get(key)
    if val is not None:
        conf[key] = val

def read_config(config_file):
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
    #
    conf = {
            'dualroot' : True,
            'rsync_opts' : None,
            'nice' : 19,
            'ionice_class' : 3,         # 0=idle
            'ionice_level' : 6,
            'sync_delay' : 300,           # seconds to delay between pending rsync requests
            'sync_list' : [],
            }

    if conf_file:
        _set_val('dualroot', conf_file, conf)
        _set_val('nice', conf_file, conf)
        _set_val('ionice_class', conf_file, conf)
        _set_val('ionice_level', conf_file, conf)
        _set_val('sync_delay', conf_file, conf)

        val = conf_file.get('rsync_opts')
        if val is not None:
            conf['rsync_opts'] = val.split()

        val = conf_file.get('sync')
        if val is not None:
            sync_list = []
            _parse_sync_list(val, sync_list)
            conf['sync_list'] = sync_list

    return conf
