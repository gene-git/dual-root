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
import os
from .utils import os_scandir
from .utils_block import device_to_uuid_mounts
from .utils_block import booted_esp_partuuid
from .utils_block import partuuid_to_device
from .utils_block import mount_to_uuid
from .utils_block import bind_mount
from .sync import sync_esp_to_alternates
from .inotify import popen_inotify_daemon

class Esp:
    """
    Info for one <esp>
    """
    # pylint: disable=R0903
    def __init__(self):
        self.partuuid = None
        self.uuid = None
        self.mount = None
        self.mount_other = []       # handle esp mounted other than /efi0, /efi1 etc
        self.dev = None
        self.mount_list = []

        self.uuid_and_mounts()

    def uuid_and_mounts(self):
        """
        For currently booted esp:
         - Get partuuid 
         - Get uuid 
        Use efibootmgr to identify booted esp
        """
        # pylint disable=R0912

        self.partuuid = booted_esp_partuuid()
        self.dev = partuuid_to_device(self.partuuid)

        if not self.dev:
            print(f'Error finding device id of partuuid: {self.partuuid}')
            return

        #
        # Get UUID and all mounts of this UUID
        #
        (self.uuid, self.mount_list) = device_to_uuid_mounts(self.dev)

        #
        # Identify mount ~ /efiN
        #
        self.mount_other = []
        for mount in self.mount_list:
            if len(mount) > 4 and mount[0:4] == '/efi':
                self.mount = mount
            else:
                self.mount_other.append(mount)

class EspInfo:
    """
    Identify esp info (UUID, mount points etc
     Support bind mounting current <esp> onto efi_mount (/boot)
     Support rsync current to alternate esp
    """
    def __init__(self, conf):
        #
        # esp is the currently booted esp.
        # Alternate esp's are listed in esp_alt
        #
        self.test = conf['test']
        self.quiet = conf['quiet']
        self.esp = Esp()
        self.esp_alt = []

        self.efi_mount = conf['efi_mount']
        self.efi_mount_uuid = None
        self.efi_mounted = False
        self.efi_uuid_correct = False
        self.euid = os.geteuid()
        self.dual_root_mount_list = []          # all /efi<n>
        self.dual_root_alt_mount_list = []      # alternate /efi<n>
        self.is_dual_root = False

        self.efi_mount_uuid = mount_to_uuid(self.efi_mount)
        self.is_efi_mounted()
        self.dual_root_mounts()

    def is_path_current_booted_esp(self, efi):
        """
        Check if efi also the currently booted esp
        """
        if not efi:
            return False

        if self.esp.mount_list and efi in self.esp.mount_list:
            return True

        return False

    def is_efi_mounted(self):
        """
        Check if efi_mount (aka /boot) mounted and if UUID we want
        default efi_mount = '/boot'
        """
        self.efi_mounted = False
        self.efi_uuid_correct = False
        if self.efi_mount in self.esp.mount_list:
            self.efi_mounted = True
            if self.efi_mount_uuid == self.esp.uuid:
                self.efi_uuid_correct = True

    def print_info(self):
        """ print useful info """
        if not self.quiet:
            print(f'Booted esp : {self.esp.dev} : {self.esp.mount_list} : {self.esp.uuid}')
            #print(f'Boot mount : {self.efi_mount} : {self.efi_mount_uuid}')

    def bind_mount_efi(self):
        """
        Bind mount current <esp> from esp.mount onto efi_mount (/boot)
            esp_mount typically /efi0 or /efi
            efi_mount typically /boot
            check that efi_mount (/boot) is not mounted already
        """
        if self.efi_mounted:
            if self.efi_uuid_correct:
                print(f'{self.esp.uuid} {self.esp.mount} already mounted on {self.efi_mount}')
            else:
                print(f'{self.efi_mount} mounted but uuid wrong - should be {self.esp.uuid}')
        elif not self.esp.mount:
            print('Not dual root, bind mount skipped: esp not mounted on /efi0,/efi1 ...')
        else:
            print(f'mount --bind {self.esp.mount} {self.efi_mount}')
            if self.euid == 0 and not self.test:
                bind_mount(self.esp.mount, self.efi_mount)
            else:
                print('Must be root to use bind mount')

    def dual_root_mounts(self):
        """
        Make a list of all the mounts names /efi<N>
         - Should we exclude booted /efi<n>
        """
        self.dual_root_mount_list = []
        self.dual_root_alt_mount_list = []

        root_scan = os_scandir('/')
        if not root_scan:
            return

        for item in root_scan:
            path = item.path
            if path.startswith('/efi') and len(path) > 4:
                self.dual_root_mount_list.append(path)
                if  not self.is_path_current_booted_esp(path):
                    self.dual_root_alt_mount_list.append(path)

        if len(self.dual_root_mount_list) > 1:
            self.is_dual_root = True


    def sync_alt_efi(self):
        """
        Sync the current booted esp to other esps
        If /efi0 is current then sync
          - /efi0/* -> /efiN for N != 0
        """
        current_efi = self.esp.mount
        all_dual_mounts = self.dual_root_mount_list
        alt_dual_mounts = self.dual_root_alt_mount_list

        if not self.is_dual_root or not all_dual_mounts:
            print('Not dual root (2 or more /efi<n> not found) -  nothing to sync')
            return

        if len(all_dual_mounts) == 1:
            this_efi = all_dual_mounts[0]
            print(f'Only 1 dual root esp found ({this_efi}) -  nothing to sync')
            return

        if len(alt_dual_mounts) == 0:
            print('No alternate dual root esp found -  nothing to sync')
            return

        sync_esp_to_alternates(current_efi, alt_dual_mounts, self.quiet, self.test)

    def sync_daemon_alt_efi(self):
        """
        Sunc Daemon:
         - Use inotify to monitor current efi and sync
           alternates whenver change detected
        """
        current_efi = self.esp.mount
        popen_inotify_daemon(self, current_efi)
