# This file manages applying configurations.

import os
import subprocess
import grp
import pwd

import asentaja
import asentaja.options
import asentaja.settings
from asentaja.settings import commands as cmd
import asentaja.system


class FileMapping:
    def __init__(self, source=None, content="", permissions=0o644, owner="root", group="root"):
        self.source = source
        self.content = content
        self.permissions = permissions
        self.owner = owner
        self.group = group

    def get_final_content(self):
        if self.source is not None:
            try:
                with open(self.source, "rt") as f:
                    return f.read()
            except Exception as e:
                print(f"Failed to read file '{self.source}' with the following exception.")
                print(e)
                return self.content
        else:
            return self.content

    def get_uid(self) -> int:
        return pwd.getpwnam(self.owner).pw_uid

    def get_gid(self) -> int:
        return grp.getgrnam(self.group).gr_gid


def apply_config():
    asentaja.options.apply_options()

    # Order here is important
    _update_packages() # Updating packages may change files / services
    _update_files() # Updating files may change services
    _update_services()

    # This is not optimal, because not every time these need to be run, but for now, it is the easiest way to make sure everything is done correctly
    if not asentaja.system.boot.disable:
        grub_cfg_path = os.path.join(asentaja.settings.filesystem_root, "boot/grub/grub.cfg")
        subprocess.run(cmd["grub-generate-config"].format(grub_cfg_path), shell=True)

        subprocess.run(cmd["mkinitcpio-generate"], shell= True)


def _update_packages():
    subprocess.run(cmd["update"], shell=True)

    previously_installed_packages = subprocess.check_output(cmd["list-installed"], shell=True).decode().split()

    packages_to_install = []
    packages_to_uninstall = []

    for pkg in asentaja.packages:
        if pkg not in previously_installed_packages:
            packages_to_install.append(pkg)

    for pkg in previously_installed_packages:
        if pkg not in asentaja.packages:
            packages_to_uninstall.append(pkg)

    if packages_to_install:
        subprocess.run(cmd["install"].format(" ".join(packages_to_install)), shell=True)

    if packages_to_uninstall:
        subprocess.run(cmd["uninstall"].format(" ".join(packages_to_uninstall)), shell=True)


def _update_services():
    previously_enabled_services = _read_list("enabled_services")

    services_to_enable = []
    services_to_disable = []

    for service in asentaja.enabled_services:
        if service not in previously_enabled_services:
            services_to_enable.append(service)

    for service in previously_enabled_services:
        if service not in asentaja.enabled_services:
            services_to_disable.append(service)

    for service in services_to_enable:
        subprocess.run(cmd["enable-service"].format(service), shell=True)

    for service in services_to_disable:
        subprocess.run(cmd["disable-service"].format(service), shell=True)

    _write_list("enabled_services", asentaja.enabled_services)


def _update_files():
    previously_written_files = _read_list("written_files")
    written_files = []

    for target, mapping in asentaja.file_mappings.items():
        file = os.path.normpath("/".join([asentaja.settings.filesystem_root, target]))
        try:
            fdir = os.path.dirname(file)

            # This will create missing directories with the same permissions as the required file.
            def create_directory(directory):
                if not os.path.isdir(directory):
                    upper_dir = os.path.dirname(directory)
                    if not os.path.isdir(upper_dir):
                        create_directory(upper_dir)
                    os.mkdir(directory)
                    os.chown(directory, mapping.get_uid(), mapping.get_gid())

            create_directory(fdir)

            with open(file, "wt") as f:
                f.write(mapping.get_final_content())
                written_files.append(file)

            os.chmod(file, mapping.permissions)
            os.chown(file, mapping.get_uid(), mapping.get_gid())

        except Exception as e:
            print(f"Failed to write contents to file '{file}' with the following exception.")
            print(e)

    for file in previously_written_files:
        if file not in written_files:
            try:
                os.remove(file)
            except Exception as e:
                print(f"Failed to remove '{file}' with the following exception.")
                print(e)

    _write_list("written_files", written_files)


def _read_list(name: str) -> list[str]:
    try:
        with open(os.path.join(asentaja.settings.filesystem_root, "var/lib/asentaja/", name), "rt") as file:
            return file.read().split()
    except Exception as e:
        print(f"Failed to read saved list '{name}' with the following exception.")
        print(e)
        return []


def _write_list(name: str, contents: list[str]):
    directory = os.path.join(asentaja.settings.filesystem_root, "var/lib/asentaja/")
    try:
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, name), "wt") as file:
            file.write("\n".join(contents))
    except Exception as e:
        print(f"Failed to write saved list '{name}' with the following exception.")
        print(e)

