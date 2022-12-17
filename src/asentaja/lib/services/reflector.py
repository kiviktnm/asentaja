import asentaja
import asentaja.options


class Reflector(asentaja.options.Option):
    def __init__(self):
        self.enable = False
        self.options = """--save /etc/pacman.d/mirrorlist
--protocol http,https
--latest 20
--sort rate"""
        super().__init__("Reflector is a service that refreshes the pacman mirrorlist.")

    def apply(self):
        if self.enable:
            asentaja.packages += [ "reflector" ]
            asentaja.enabled_services += [ "reflector.service" ]
            asentaja.file_mappings["/etc/xdg/reflector/reflector.conf"] = asentaja.FileMapping(content=self.options)

