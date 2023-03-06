.. SPDX-License-Identifier: MIT

.. _install:

======================================
Dual Root - Install
======================================


Docs
-----
To build pdf or html version of the readme::


    cd docs
    make html
    make latexpdf


This will create _build/latex/dual-root.pdf
and a set of html pages under _build/html

duel-root-tool 
--------------

On arch simpley build and install the package. The PKGBUILD is on AUR and under packaging directory.

Otherwise install dual-root-tool

    cp dual-root-tool /usr/bin/

Bind mount service file ::

    cp bind-mount-efi.service /etc/systemd/system/
      or
    cp bind-mount-efi.service /usr/lib/systemd/system

    systemctl enable bind-mount-efi.service
    systemctl start bind-mount-efi.service

Remember to ensure that the <esp> get mounted before bind mount service add mount
options x-systemd.before=bind-mount-efi.service to each of the <esp> mount lines::

    UUID=... /efi0 vfat rw,...,x-systemd.before=bind-mount-efi.service 0 0
    UUID=... /efi1 vfat rw,...,x-systemd.before=bind-mount-efi.service 0 0

 

