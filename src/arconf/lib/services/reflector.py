import arconf
import arconf.options


class Reflector(arconf.options.Option):
    def __init__(self):
        self.enable = False
        self.options = """--save /etc/pacman.d/mirrorlist
--protocol http,https
--latest 20
--sort rate"""
        super().__init__("Reflector is a service that refreshes the pacman mirrorlist.")

    def apply(self):
        if self.enable:
            arconf.packages += [ "reflector" ]
            arconf.enabled_services += [ "reflector.service" ]
            arconf.file_mappings["/etc/xdg/reflector/reflector.conf"] = arconf.FileMapping(content=self.options)

