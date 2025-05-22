# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com
"""
  Dual Root Support Utils
"""
import os
from .utils import run_cmd


def device_to_uuid_mounts(dev: str) -> tuple[str, list[str]]:
    """
    Support Esp class
    For block device /dev/xxx
     - Get the UUID
     - Get list of all mount points
    """

    uuid = ''
    mounts: list[str] = []

    if not dev:
        return (uuid, mounts)

    pargs = ['/usr/bin/lsblk', '-no', 'UUID,MOUNTPOINTS', dev]
    result_lines = run_cmd(pargs)

    if not result_lines:
        print(f'Failed to find uuid of {dev}')
        return (uuid, mounts)

    for line in result_lines:
        item = line.split()
        if len(item) > 1:
            uuid = item[0]
            mount = item[1]
        else:
            mount = item[0]
        mounts.append(mount)

    return (uuid, mounts)


def booted_esp_partuuid() -> str:
    """
    Identify partuuid of currently booted esp
     - Run efibootmgr to get partuuid
    """
    partuuid = ''

    pargs = ['/usr/bin/efibootmgr']
    result_lines = run_cmd(pargs)
    if not result_lines:
        print('Failed to run efibootmgr')
        return partuuid

    #
    # Find current bootnum
    #
    bootnum = ''
    for row in result_lines:
        if row.startswith('BootCurrent:'):
            bootnum = row.split()[1]
            break

    if not bootnum:
        # should never happen
        print('Failed to find current bootnum')
        return partuuid

    #
    # Find current boot info from bootnu
    #
    thisboot = f'Boot{bootnum}'
    bootinfo = ''
    for row in result_lines:
        if row.startswith(thisboot):
            bootinfo = row
            break

    if not bootinfo:
        print('Failed to find efibootmgr boot line with partuuid')
        return partuuid

    #
    # Extract the partuuid
    #
    # Line to parse: Bootxxx* <text> HD(n,GPT,partuuid,xxx,..)
    #
    lsplit = bootinfo.split(',')
    if len(lsplit) >= 2:
        partuuid = lsplit[2]

    if not partuuid:
        print('Failed to find booted esp partuuid')

    return partuuid


def partuuid_to_device(partuuid: str) -> str:
    """
    Get device path associated with a partuuid.

    Returns:
        str:
        /dev/device_name
    """
    device = ''
    by_puid_path = f'/dev/disk/by-partuuid/{partuuid}'
    if os.path.islink(by_puid_path):
        device = os.readlink(by_puid_path)
        device = os.path.basename(device)
        device = f'/dev/{device}'
    return device


def mount_to_uuid(mount_dir: str) -> str:
    """
    Get UUID of device mounted at mount_dir
    """
    uuid = ''
    if not mount_dir:
        return uuid

    pargs = ['/usr/bin/lsblk', '-lno', 'UUID,MOUNTPOINTS']
    result_lines = run_cmd(pargs)

    if not result_lines:
        print(f'Failed to find any uuid of {mount_dir}')
        return uuid

    for item in result_lines:
        items = item.split()
        if len(items) > 1:
            (this_uuid, this_mount) = items
            if this_mount == mount_dir:
                uuid = this_uuid
                break
    return uuid


def bind_mount(src_dir: str, dest_dir: str):
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
    result = run_cmd(pargs)
    if not result:
        print(f'Bind Mount failed {src_dir} -> {dest_dir}')
        return not okay
    return okay
