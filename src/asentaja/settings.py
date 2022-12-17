# This file contains settings for asentaja itself.

# Commands that asentaja will use to manage packages and services
commands: dict[str, str]= {}
commands["update"] = "pacman -Syu"
commands["install"] = "pacman -S {}"
commands["uninstall"] = "pacman -Rs {}"
commands["list-installed"] = "pacman -Qe"
commands["enable-service"] = "systemctl enable {}"
commands["disable-service"] = "systemctl disable {}"
commands["grub-generate-config"] = "grub-mkconfig -o {}"
commands["mkinitcpio-generate"] = "mkinitcpio -P"

# Default paths for asentaja
filesystem_root = "/"

