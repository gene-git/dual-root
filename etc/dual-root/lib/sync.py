# SPDX-License-Identifier: MIT
# Copyright (c) 2023, Gene C
"""
  Dual Root Support Utils
"""
import os
from .utils import run_prog
from .utils_block import mount_to_uuid

def sync_one(sync_item, quiet, test):
    """
    Sync one SyncItem 
     - source/dest/exclusionsitems use rsync notation 
     - e.g. include trailing "/" if needed etc
    """
    rsync_opts = []
    if test:
        rsync_opts += ['-nv']

    for excl in sync_item.excl_list:
        rsync_opts += [f'--exclude={excl}']

    rsync_opts += ['-axHAX', '--exclude=/lost+found/', '--delete']
    rsync = ['/usr/bin/rsync'] + rsync_opts

    for dest in sync_item.dst_list:
        pargs = rsync + [f'{sync_item.src}', f'{dest}']
        if not quiet:
            cmd = ' '.join(pargs)
            print(cmd)

        [retc, out, err] = run_prog(pargs)
        if retc != 0:
            print(f'rsync failed: {sync_item.source} -> {dest}')
            print(err)
        elif test and out:
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
        print(f'Misformed sync item {item}. Should be [src, dest_list, excl_list]')
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
        print(f' *Error* : Watch source {src} doesnt exist')
        return False

    uuid_src = None
    if os.path.ismount(src):
        uuid_src = mount_to_uuid(src)

    for dest in dest_list:
        if os.path.exists(dest):
            if src_is_dir :
                if not os.path.isdir(dest):
                    print(f' *Error* : Watch {src} is dir, dest {dest} must be dir')
                    return False
        else:
            print(f' *Error* : Watch {src} to non-existent {dest}')
            return False

        if uuid_src and os.path.ismount(dest):
            uuid_dest = mount_to_uuid(dest)
            if uuid_src == uuid_dest:
                print(f' *Error* : Watch dir {src} is same filesystem as dest {dest}')
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
