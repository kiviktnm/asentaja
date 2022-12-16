import os

import arconf
import arconf.programs
import arconf.settings
import arconf.services
import arconf.system

arconf.settings.commands["install"] = "echo Installing: {}"
arconf.settings.commands["uninstall"] = "echo Uninstalling: {}"
arconf.settings.commands["update"] = "echo Updating"
arconf.settings.commands["list-installed"] = "echo reflector abc bcd"
arconf.settings.commands["enable-service"] = "echo Enabling service {}"
arconf.settings.commands["disable-service"] = "echo Disabling service {}"
arconf.settings.commands["grub-generate-config"] = "echo Generating grub config to {}"

arconf.settings.filesystem_root = os.path.join(os.path.dirname(__file__), "../output")

arconf.packages += [ "ijk", "abc" ]
arconf.enabled_services += [ ]
arconf.file_mappings["/home/kk/helloworld.py"] = arconf.FileMapping(content="print(\"Hello, World!\")", permissions=0o744, owner="kk", group="users")
arconf.file_mappings["/root/helloworld.py"] = arconf.FileMapping(content="print(\"Hello, World!\")", permissions=0o744)
arconf.file_mappings["test.txt"] = arconf.FileMapping(source="src/source.txt")

arconf.services.reflector.enable = True

arconf.system.boot.kernel_parameters += [ "quiet", "splash" ]

arconf.system.amd.enable = True
arconf.system.amd.enable32bit = True
arconf.system.amd.ati = True

