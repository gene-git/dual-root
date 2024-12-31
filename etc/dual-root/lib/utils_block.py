# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com
"""
  Dual Root Support Utils
"""
import os
from .utils import run_prog

def device_to_uuid_mounts(dev):
    """
    Support Esp class
    For block device /dev/xxx
     - Get the UUID 
     - Get list of all mount points 
    """
    if not dev:
        return None

    pargs = ['/usr/bin/lsblk', '-no', 'UUID,MOUNTPOINTS', dev]
    [retc, result, _err] = run_prog(pargs)

    if retc != 0:
        print(f'Failed to find uuid of {dev}')
        return None

    uuid = None

    result = result.splitlines()

    mounts = []
    for item in result:
        item = item.split()
        if len(item) > 1:
            uuid = item[0]
            mount = item[1]
        else:
            mount = item[0]
        mounts.append(mount)
    return (uuid, mounts)

def booted_esp_partuuid():
    """
    Identify partuuid of currently booted esp
     - Run efibootmgr to get partuuid
    """

    partuuid = None
    pargs = ['/usr/bin/efibootmgr']
    [retc, stdout, _stderr] = run_prog(pargs)
    if retc != 0:
        print('Failed to run efibootmgr')
        return None

    #
    # Find current bootnum
    #
    stdout = stdout.splitlines()
    bootnum = None
    for row in stdout:
        if row.startswith('BootCurrent:'):
            bootnum = row.split()[1]
            break

    if not bootnum:
        # should never happen
        print('Failed to find current bootnum')
        return None

    #
    # Find current boot info from bootnu
    #
    thisboot = f'Boot{bootnum}'
    bootinfo = None
    for row in stdout:
        if row.startswith(thisboot):
            bootinfo = row
            break

    if not bootinfo:
        print('Failed to find efibootmgr boot line with partuuid')
        return None

    #
    # Extract the partuuid
    #
    # Line to parse: Bootxxx* <text> HD(n,GPT,partuuid,xxx,..)
    #
    partuuid = None
    lsplit = bootinfo.split(',')
    if len(lsplit) >= 2:
        partuuid = lsplit[2]

    if not partuuid:
        print('Failed to find booted esp partuuid')

    return partuuid

def partuuid_to_device(partuuid):
    """
    Get device associated with a partuuid
    """
    device = None
    by_puid_path = f'/dev/disk/by-partuuid/{partuuid}'
    if os.path.islink(by_puid_path):
        device = os.readlink(by_puid_path)
        device = os.path.basename(device)
        device = f'/dev/{device}'
    return device

def mount_to_uuid(mount_dir):
    """
    Get UUID of device mounted at mount_dir
    """
    if not mount_dir:
        return None

    pargs = ['/usr/bin/lsblk', '-lno', 'UUID,MOUNTPOINTS']
    [retc, result, _err] = run_prog(pargs)

    if retc != 0:
        print(f'Failed to find any uuid of {mount_dir}')
        return None

    result = result.splitlines()

    uuid = None
    for item in result:
        items = item.split()
        if len(items) > 1:
            (this_uuid, this_mount) = items
            if this_mount == mount_dir:
                uuid = this_uuid
                break

    return uuid

def bind_mount(src_dir, dest_dir):
    """
    Bind mount src_dir onto dest_dir
     - must be root 
     - does not check if dest_dir mounted already
     - NB os.path.ismount(path) is not reliable for bind mounts on same filesys
       So we don't use this to check if already mounted. Caller 
       checks (see is_efi_mounted() method)
    """
    okay = True
    pargs = ['/usr/bin/mount', '--bind', src_dir, dest_dir]
    [retc, _out, err] = run_prog(pargs)
    if retc != 0:
        print(f'Bind Mount failed {src_dir} -> {dest_dir}: {err}')
        return not okay
    return okay
