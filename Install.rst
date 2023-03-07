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
sphinx (aka python-sphinx) must be installed

duel-root-tool 
--------------

On arch simply build and install the package. The PKGBUILD is on AUR and under packaging directory.

Otherwise manually install dual-root-tool, run the installer script as root with the 
destination directory set to */* ::

    ./scripts/do-install / 

This installs into ::

    /etc/dual-root 
    /usr/share/dual-root
    /usr/share/licenses/dual-root/

    /usr/bin/dual-root-tool
    /usr/lib/systemd/system/bind-mount-efi.service
    /usr/lib/systemd/system/dual-root-syncd.service

/usr/bin/dual-root is now a symlink to */etc/dual-root/dual-root-tool*
This allows us to organize the code a little better. 

As usual to activate the bind service::

    systemctl enable bind-mount-efi.service
    systemctl start bind-mount-efi.service

And for the inotify based sync daemon::

    systemctl enable bind-mount-efi.service
    systemctl start bind-mount-efi.service


Remember to ensure that the <esp>s get mounted before bind mount service.
That is done using systemd mount option in fstab.
Add option *x-systemd.before=bind-mount-efi.service* to each of the <esp> mount lines::

    UUID=... /efi0 vfat rw,...,x-systemd.before=bind-mount-efi.service 0 0
    UUID=... /efi1 vfat rw,...,x-systemd.before=bind-mount-efi.service 0 0

