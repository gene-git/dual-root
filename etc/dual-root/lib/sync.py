# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com
"""
  Dual Root Support Utils
"""
from typing import (List)
import os
from .utils import run_prog
from .utils_block import mount_to_uuid


def rsync_options_final(opts_in: List[str], test: bool = False) -> List[str]:
    """
    Given starting rsync options return full list of options to use.

    Combiine caller provided with needed options.

    -axHAX --times --no-specials --atimes --open-noatime --delete
    """
    opts: List[str] = []
    if opts_in:
        opts += opts_in

    opts += ['--times', '--no-specials', '--atimes', '--open-noatime']
    opts += ['--delete']

    if test:
        opts += ['-n', '-v']

    #
    # Duplicate options are benign.
    # We remove obvious dups by catching
    # identical elements in the list.
    #  - we miss short vs long of same option
    #
    rsync_opts = list(set(opts))

    #
    # Split shor/long options and make each unique.
    # All options with values take form : --xxx=yyy
    # and will be kept together here.
    # All short options are "-?" (no double dashes)
    #
    short_opts: List[str] = []
    long_opts: List[str] = []
    for opt in rsync_opts:
        if opt[0:2] == '--':
            long_opts.append(opt)
        else:
            for letter in opt[1:]:
                short = '-' + letter
                short_opts.append(short)

    if short_opts:
        short_opts = list(set(short_opts))

    if long_opts:
        long_opts = list(set(long_opts))

    rsync_opts = short_opts + long_opts

    return rsync_opts


def sync_one(sync_item, quiet):
    """
    Sync one SyncItem
     - source/dest/exclusionsitems use rsync notation
     - e.g. include trailing "/" if needed etc
     - rsync_opts_in is either None or list of options
    """
    rsync_item = sync_item.rsync_item

    rsync_opts = rsync_item.rsync_opts
    rsync_opts += ['--exclude=/lost+found/']
    for excl in rsync_item.excl:
        rsync_opts += [f'--exclude={excl}']

    rsync = ['/usr/bin/rsync'] + rsync_opts

    for dest in rsync_item.dst:
        pargs = rsync + [f'{rsync_item.src}', f'{dest}']
        if not quiet:
            cmd = ' '.join(pargs)
            print(cmd)

        (retc, out, err) = run_prog(pargs)
        if retc != 0:
            print(f'rsync failed: {rsync_item.src} -> {dest}')
            print(err)
        elif sync_item.test and out:
            print(out)


def _check_sync_item(item, all_src, all_dst):
    """
    Sanity check one itm in sync list
     - Avoid duplicates
     - Source cannot be dest
       If mount point, check for UUID
     - Source and dest must exist
     - input here lists - not SyncItems
    """
    # pylint: disable=R0911,R0912
    if len(item) != 3:
        print(f'Malformed sync item {item}.')
        print('Should be (src, dest_list, excl_list)')
        return False

    src = item[0]
    dest_list = item[1]

    if src in all_src:
        print(f'*Error* Duplicate watch source {src}')
        return False

    if src in all_dst:
        print(f'*Error*  watch source {src} cannot also be destination')
        return False

    src_is_dir = False
    if os.path.exists(src):
        if os.path.isdir(src):
            src_is_dir = True
    else:
        print(f' *Error*: Watch source {src} doesnt exist')
        return False

    uuid_src = None
    if os.path.ismount(src):
        uuid_src = mount_to_uuid(src)

    for dest in dest_list:
        if os.path.exists(dest):
            if src_is_dir:
                if not os.path.isdir(dest):
                    err = f'Watch {src} is dir, dest {dest} must be dir'
                    print(f' *Error*: {err}')
                    return False
        else:
            print(f' *Error*: Watch {src} to non-existent {dest}')
            return False

        if uuid_src and os.path.ismount(dest):
            uuid_dest = mount_to_uuid(dest)
            if uuid_src == uuid_dest:
                err = f' Watch dir {src} is same filesystem as dest {dest}'
                print(f' *Error*: {err}')
                return False
    return True


def check_sync_list(sync_list):
    """
    Sanity check sync list
       sync_list has each element ~ [src, dst, excl]
    """

    all_dest = []
    all_src = []
    for item in sync_list:
        all_src.append(item[0])
        all_dest.append(item[1])

    num_items = len(sync_list)
    for item in sync_list:
        all_src_but_me = []
        if num_items > 1:
            all_src_but_me = all_src.copy()
            all_src_but_me.remove(item[0])
        okay = _check_sync_item(item, all_src_but_me, all_dest)
        if not okay:
            return False
    return True
