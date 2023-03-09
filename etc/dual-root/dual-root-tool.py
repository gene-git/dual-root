#!/usr/bin/python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2023, Gene C
"""
 Dual Root Tool
  Identify which <esp> was used to boot the currently running system.

  - identify which <esp> was used to boot current system
  - support bind mounting this <esp> onto /boot
  - support rsyncing this onto the alternate <esp>

 Required
   python (> 3.9), efibootmgr, mount, rsync

 Should a low level tool be in python? Probably not, but it gets a working tool done
 reasonably safely and quickly.  This is far too complex for a bash script, but we
 should probably make a statically linked C++ or C version at some point.

 But for now this works.

 GC 2023
"""
import argparse
from lib import EspInfo

def parse_args():
    """
    Command line requests
    """
    desc = 'dual-root-tool : dual <esp> management tool'

    bind = False
    sync = False
    syncd = False
    test = False
    quiet = False
    config_file = '/etc/dual-root/sync-daemon.conf'
    efi_mount = '/boot'

    par = argparse.ArgumentParser(description=desc)
    par.add_argument('-b', '--bind', action='store_true', help='Bind mount active esp to efi mount')
    par.add_argument('-s', '--sync', action='store_true', help='Sync active efi to alternate')
    par.add_argument('-sd','--syncd', action='store_true', help='Start sync daemon using inotify')
    par.add_argument('-t', '--test', action='store_true', help='Test mode')
    par.add_argument('-q', '--quiet', action='store_true', help='Quiet mode')
    par.add_argument('-c', '--conf', default=config_file,
                     help='Sync daemon config ')
    par.add_argument('efi_mount', nargs='?', default=efi_mount,
                     help=f'Where to bind mount active esp ({efi_mount})')
    parsed = par.parse_args()
    if parsed:
        if parsed.bind:
            bind = parsed.bind
        if parsed.sync:
            sync = parsed.sync
        if parsed.syncd:
            syncd = parsed.syncd
            sync = True
        if parsed.test:
            test = parsed.test
        if parsed.quiet:
            quiet = parsed.quiet
        if parsed.conf:
            config_file = parsed.conf

        efi_mount = parsed.efi_mount

    conf = {
            'bind'   : bind,
            'sync'   : sync,
            'syncd'  : syncd,
            'test'   : test,
            'quiet'  : quiet,
            'config_file'  : config_file,
            'efi_mount' : efi_mount,
            }
    return conf

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
    conf = parse_args()

    esp = EspInfo(conf)
    esp.print_info()

    if not esp.okay:
        return

    if conf["bind"]:
        esp.bind_mount_efi()

    if conf["sync"]:
        if conf["syncd"]:
            esp.sync_daemon_start()
        else:
            esp.sync_all_items()


if __name__ == '__main__':
    main()
