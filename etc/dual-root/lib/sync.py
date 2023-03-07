# SPDX-License-Identifier: MIT
# Copyright (c) 2023, Gene C
"""
  Dual Root Support Utils
"""
from .utils import run_prog

def sync_esp_to_alternates(current_efi, alt_efis, quiet, test):
    """
    Sync booted efi to 1 or more alternates
    """
    rsync_opts = []
    if test:
        rsync_opts += ['-nv']
    rsync_opts += ['-axHAX', '--exclude=/lost+found/', '--delete']
    rsync = ['/usr/bin/rsync'] + rsync_opts

    for efi in alt_efis:
        pargs = rsync + [f'{current_efi}/', f'{efi}/']
        if not quiet:
            cmd = ' '.join(pargs)
            print(cmd)

        [retc, out, err] = run_prog(pargs)
        if retc != 0:
            print(f'rsync failed: {current_efi}/ -> {efi}/')
            print(err)
        elif test and out:
            print(out)
