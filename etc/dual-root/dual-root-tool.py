#!/usr/bin/python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
 Dual Root Tool
  Identify which <esp> was used to boot the currently running system.

  - identify which <esp> was used to boot current system
  - support bind mounting this <esp> onto /boot
  - support rsyncing this onto the alternate <esp>

 Required
   python (> 3.9), efibootmgr, mount, rsync

 Should a low level tool be in python? Probably not, but it gets a
 working tool done reasonably safely and quickly.  This is far too
 complex for a bash script, but we should probably make a statically
 linked C++ or C version at some point.

 But for now this works.

 GC 2023
"""
# pylint: disable=invalid-name
from lib import EspInfo


def main():
    """
    Tool to :
        - identify currently booted <esp>
        - bind mount currently booted <esp> onto /boot
        - sync currently booted <esp> on to the other <esp>
    Args :
         -h for help:
         no arguments : print out information about currenntly booted efi
         --bind, --sync, --syncd, --test, --quiet. --conf CONF
    """
    esp = EspInfo()

    if not esp.okay:
        return

    esp.print_info()

    if esp.conf.bind:
        esp.bind_mount_efi()

    if esp.conf.sync:
        esp.sync_all_items()

    if esp.conf.syncd:
        esp.sync_daemon_start()


if __name__ == '__main__':
    main()
