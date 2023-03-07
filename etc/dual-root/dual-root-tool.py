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
    test = False
    quiet = False
    efi_mount = '/boot'

    par = argparse.ArgumentParser(description=desc)
    par.add_argument('-b', '--bind', action='store_true', help='Bind mount active esp to efi mount')
    par.add_argument('-s', '--sync', action='store_true', help='Sync active efi to alternate')
    par.add_argument('-t', '--test', action='store_true', help='Test mode')
    par.add_argument('-q', '--quiet', action='store_true', help='Quiet mode')
    par.add_argument('efi_mount', nargs='?', default=efi_mount,
                     help=f'Where to bind mount active esp ({efi_mount})')
    parsed = par.parse_args()
    if parsed:
        if parsed.bind:
            bind = parsed.bind
        if parsed.sync:
            sync = parsed.sync
        if parsed.test:
            test = parsed.test
        if parsed.quiet:
            quiet = parsed.quiet

        efi_mount = parsed.efi_mount

    conf = {
            'bind'   : bind,
            'sync'   : sync,
            'test'   : test,
            'quiet'  : quiet,
            'efi_mount' : efi_mount,
            }

    return conf

#import pdb
def main():
    """
    Tool to :
        - identify currently booted <esp>
        - bind mount currently booted <esp> onto /boot
        - sync currently booted <esp> on to the other <esp>
    Arhg :
         no arguments : print out information about currenntly booted efi
         -b           : bind mount currently booted <esp> onto "mount" - default is /boot
         -s           : sync currentnly booted <esp> to the other on
         -h           : help
         efi_mount     : where to mount the active esp - default is /boot
    """
    #pdb.set_trace()
    conf = parse_args()

    esp = EspInfo(conf)
    esp.print_info()

    if conf["bind"]:
        esp.bind_mount_efi()
    if conf["sync"]:
        esp.sync_alt_efi()

if __name__ == '__main__':
    main()
