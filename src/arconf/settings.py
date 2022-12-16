# This file contains settings for arconf itself.

# Commands that arconf will use to manage packages and services
commands: dict[str, str]= {}
commands["update"] = "pacman -Syu"
commands["install"] = "pacman -S {}"
commands["uninstall"] = "pacman -Rs {}"
commands["list-installed"] = "pacman -Qe"
commands["enable-service"] = "systemctl enable {}"
commands["disable-service"] = "systemctl disable {}"
commands["grub-generate-config"] = "grub-mkconfig -o {}"
commands["mkinitcpio-generate"] = "mkinitcpio -P"

# Default paths for arconf
filesystem_root = "/"

