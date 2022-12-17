import os

import asentaja
import asentaja.programs
import asentaja.settings
import asentaja.services
import asentaja.system

asentaja.settings.commands["install"] = "echo Installing: {}"
asentaja.settings.commands["uninstall"] = "echo Uninstalling: {}"
asentaja.settings.commands["update"] = "echo Updating"
asentaja.settings.commands["list-installed"] = "echo reflector abc bcd"
asentaja.settings.commands["enable-service"] = "echo Enabling service {}"
asentaja.settings.commands["disable-service"] = "echo Disabling service {}"
asentaja.settings.commands["grub-generate-config"] = "echo Generating grub config to {}"

asentaja.settings.filesystem_root = os.path.join(os.path.dirname(__file__), "../output")

asentaja.packages += [ "ijk", "abc" ]
asentaja.enabled_services += [ ]
asentaja.file_mappings["/home/kk/helloworld.py"] = asentaja.FileMapping(content="print(\"Hello, World!\")", permissions=0o744, owner="kk", group="users")
asentaja.file_mappings["/root/helloworld.py"] = asentaja.FileMapping(content="print(\"Hello, World!\")", permissions=0o744)
asentaja.file_mappings["test.txt"] = asentaja.FileMapping(source="src/source.txt")

asentaja.services.reflector.enable = True

asentaja.system.boot.kernel_parameters += [ "quiet", "splash" ]

asentaja.system.amd.enable = True
asentaja.system.amd.enable32bit = True
asentaja.system.amd.ati = True

